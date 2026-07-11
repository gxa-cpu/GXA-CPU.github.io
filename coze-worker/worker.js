const BOT_ID = '7658501651363954697';
const PAT = 'pat_4L4arWbpPLj6JIOVXG2oTT50UtGgOqn5muBUzdACPaeD8LE2HOJAVNPRUaOHyhdK';
const COZE_BASE = 'https://api.coze.cn';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    try {
      const { message, conversation_id } = await request.json();

      // Step 1: Create chat
      const chatBody = {
        bot_id: BOT_ID,
        user_id: 'web_visitor_' + Math.random().toString(36).slice(2, 8),
        stream: false,
        auto_save_history: true,
        additional_messages: [
          { role: 'user', content: message, content_type: 'text' }
        ]
      };
      if (conversation_id) {
        chatBody.conversation_id = conversation_id;
      }

      const chatResp = await fetch(COZE_BASE + '/v3/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + PAT
        },
        body: JSON.stringify(chatBody)
      });
      const chatData = await chatResp.json();

      if (chatData.code !== 0) {
        console.error('Create chat error:', JSON.stringify(chatData));
        return new Response(JSON.stringify({ error: 'chat_create_failed', detail: chatData.msg }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }

      const chatId = chatData.data.id;
      const convId = chatData.data.conversation_id;
      let status = chatData.data.status;

      // Step 2: Poll for completion (max 30s)
      let attempts = 0;
      while (status !== 'completed' && status !== 'failed' && attempts < 30) {
        await new Promise(function(r) { setTimeout(r, 1000); });
        const pollResp = await fetch(
          COZE_BASE + '/v3/chat/retrieve?chat_id=' + chatId + '&conversation_id=' + convId,
          { headers: { 'Authorization': 'Bearer ' + PAT } }
        );
        const pollData = await pollResp.json();
        if (pollData.code === 0 && pollData.data) {
          status = pollData.data.status;
        }
        attempts++;
      }

      if (status !== 'completed') {
        return new Response(JSON.stringify({ error: 'timeout', status: status }), {
          status: 504,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }

      // Step 3: Get messages
      const msgResp = await fetch(
        COZE_BASE + '/v1/chat/message/list?chat_id=' + chatId + '&conversation_id=' + convId,
        { headers: { 'Authorization': 'Bearer ' + PAT } }
      );
      const msgData = await msgResp.json();

      let answer = '';
      if (msgData.code === 0 && msgData.data) {
        for (let i = 0; i < msgData.data.length; i++) {
          const m = msgData.data[i];
          if (m.role === 'assistant' && m.type === 'answer') {
            answer = m.content;
            break;
          }
        }
      }

      if (!answer) {
        answer = '抱歉，我没理解你的意思，能再说一遍吗？';
      }

      return new Response(JSON.stringify({
        answer: answer,
        conversation_id: convId
      }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });

    } catch (err) {
      console.error('Worker error:', err);
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }
  }
};
