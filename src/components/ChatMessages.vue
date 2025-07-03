<template>
  <div class="chat-messages" ref="messagesContainer">
    <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
      <div 
        class="message" 
        :class="{ 
          'user-message': message.type === 'user', 
          'ai-message': message.type === 'assistant' 
        }"
      >
        <div class="message-avatar">
          <el-icon v-if="message.type === 'user'" size="20" class="user-icon">
            <User />
          </el-icon>
          <div v-else class="ai-avatar">AI</div>
        </div>
        
        <div class="message-content">
          <div class="message-text">
            <!-- 显示图片 -->
            <img 
              v-if="message.imageUrl" 
              :src="message.imageUrl" 
              alt="上传的图片" 
              class="message-image"
            />
            <!-- 显示文本内容 -->
            <div v-html="formatAnswer(message.content)"></div>
          </div>
          
          <!-- AI思考过程 -->
          <div v-if="message.type === 'assistant' && message.thinking" class="thinking-process">
            <div class="thinking-header">
              <el-icon size="16"><DataAnalysis /></el-icon>
              <span>思考过程</span>
            </div>
            <div class="thinking-content">{{ message.thinking }}</div>
          </div>
          
          <!-- 信息来源 -->
          <div v-if="message.sources && message.sources.length > 0" class="message-sources">
            <div class="sources-header">
              <el-icon size="16"><DocumentCopy /></el-icon>
              <span>信息来源</span>
            </div>
            <div class="sources-list">
              <div v-for="(source, idx) in message.sources" :key="idx" class="source-item">
                {{ source }}
              </div>
            </div>
          </div>
          
          <div class="message-footer">
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            <div v-if="message.type === 'assistant'" class="message-actions">
              <el-tooltip content="复制">
                <el-button 
                  type="text" 
                  :icon="DocumentCopy" 
                  size="small"
                  @click="$emit('copyText', message.content)"
                />
              </el-tooltip>
              <el-tooltip content="点赞">
                <el-button 
                  type="text" 
                  :icon="Star" 
                  size="small"
                  @click="$emit('likeMessage', index)"
                />
              </el-tooltip>
              <el-tooltip content="重新生成">
                <el-button 
                  type="text" 
                  :icon="Refresh" 
                  size="small"
                  @click="$emit('regenerateResponse', index)"
                />
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入中状态 -->
    <div v-if="loading" class="message ai-message typing-message">
      <div class="message-avatar">
        <div class="ai-avatar">AI</div>
      </div>
      <div class="message-content">
        <div class="typing-indicator">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span class="typing-text">AI 正在思考中...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  User, DocumentCopy, Star, Refresh, DataAnalysis 
} from '@element-plus/icons-vue'

defineProps({
  messages: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['copyText', 'likeMessage', 'regenerateResponse'])

const messagesContainer = ref(null)

// 格式化时间
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 格式化答案
function formatAnswer(text) {
  return text.replace(/\n/g, '<br>')
}

defineExpose({
  messagesContainer
})
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
}

.message {
  display: flex;
  gap: 16px;
  max-width: 100%;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 8px 20px;
}

.ai-message .message-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #1f2937;
  border-radius: 20px 20px 20px 8px;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-icon {
  background: #f3f4f6;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.ai-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.message-content {
  max-width: 70%;
  padding: 16px 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.thinking-process {
  margin-top: 16px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
}

.thinking-content {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.message-sources {
  margin-top: 16px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.05);
  border-radius: 8px;
  border-left: 3px solid #22c55e;
}

.sources-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #22c55e;
  margin-bottom: 8px;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.source-item {
  font-size: 13px;
  color: #6b7280;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.ai-message .message-time {
  color: #9ca3af;
}

.message-actions {
  display: flex;
  gap: 4px;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.message-actions:hover {
  opacity: 1;
}

.typing-message {
  opacity: 0.8;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

.typing-text {
  font-size: 14px;
  color: #6b7280;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
