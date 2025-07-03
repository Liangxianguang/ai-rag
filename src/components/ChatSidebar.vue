<template>
  <div class="chat-sidebar">
    <div class="sidebar-header">
      <h3>对话历史</h3>
      <el-button
        type="primary"
        :icon="Plus"
        @click="$emit('newChat')"
        class="new-chat-btn"
      >
        新对话
      </el-button>
    </div>
    <div class="chat-sessions">
      <div
        v-for="(session, index) in sessions"
        :key="index"
        class="session-item"
        :class="{ active: index === currentIndex }"
        @click="$emit('switchSession', index)"
      >
        <div class="session-content">
          <div class="session-title">
            {{ session.title || '新对话' }}
          </div>
          <div class="session-time">
            {{ formatDate(session.createdAt) }}
          </div>
        </div>
        <div class="session-actions">
          <el-button
            type="danger"
            :icon="Delete"
            size="small"
            class="delete-btn"
            @click.stop="$emit('deleteSession', index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, Delete } from '@element-plus/icons-vue'

defineProps({
  sessions: {
    type: Array,
    required: true
  },
  currentIndex: {
    type: Number,
    required: true
  }
})

defineEmits(['newChat', 'switchSession', 'deleteSession'])

// 格式化日期
function formatDate(timestamp) {
  const date = new Date(timestamp)
  const today = new Date()
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  
  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}
</script>

<style scoped>
.chat-sidebar {
  width: 320px;
  background: none;
  border-radius: 0 !important;
  box-shadow: none !important;
  border-right: 1px solid rgba(255, 255, 255, 0.795);
  display: flex;
  flex-direction: column;
  height: 100%;
  margin: 0 !important;
  padding: 0 !important;
}

.sidebar-header {
  padding: 24px 20px 20px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: none;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.new-chat-btn {
  border-radius: 8px;
  font-size: 14px;
}

.chat-sessions {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  margin-bottom: 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  background: linear-gradient(90deg, #e0e7ff 0%, #f0f4ff 100%);
  /* 柔和蓝紫色渐变 */
}

.session-item:hover {
  background: linear-gradient(90deg, #c7d2fe 0%, #e0e7ff 100%);
  border-color: #a5b4fc;
  transform: translateX(4px);
}

.session-item.active {
  background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
  border-color: #6366f1;
  color: #fff;
}
.session-item.active .session-title,
.session-item.active .session-time {
  color: #fff;
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.delete-btn {
  border-radius: 6px;
  padding: 4px;
  min-height: auto;
}

.delete-btn:hover {
  background: #fee2e2;
  border-color: #fecaca;
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 12px;
  color: #6b7280;
}
</style>
