css = '''
<style>
  .chat-container {
    max-width: 800px;
    margin: 0 auto;
    background-color: #f5f5f5;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .chat-message {
    padding: 1rem 1.5rem;
    border-radius: 1.5rem;
    margin: 1rem 2rem;
    display: flex;
    transition: all 0.3s ease;
    max-width: 70%;
  }

  .chat-message:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }

  .chat-message.user {
    background-color: #475063;
    margin-left: auto;
    background-image: linear-gradient(to right, #475063, #6f7b8b);
  }

  .chat-message.bot {
    background-color: #2b313e;
    margin-right: auto;
    background-image: linear-gradient(to left, #2b313e, #3e4757);
  }

  .chat-message .avatar {
    width: 15%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .chat-message .avatar img {
    max-width: 48px;
    max-height: 48px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .chat-message .message {
    width: 85%;
    padding: 0.5rem 1rem;
    color: #fff;
    font-family: 'Roboto', sans-serif;
    font-size: 16px;
    line-height: 1.5;
  }
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/yscC3P9/original-3cfdbabadfd8f92aed97b0c0b57c6b89.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/FgmnMNd/pngtree-user-icon-vector-png-image-12276906.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
