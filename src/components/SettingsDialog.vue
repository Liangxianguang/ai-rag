<template>
  <el-dialog v-model="localShowSettings" title="AI 助手设置" width="500px">
    <el-form label-width="120px">
      <el-form-item label="使用模式">
        <el-radio-group v-model="localSettings.useLocalModel">
          <el-radio :label="true">本地模型 (Ollama)</el-radio>
          <el-radio :label="false">远程 API</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 本地模型设置 -->
      <template v-if="localSettings.useLocalModel">
        <el-form-item label="Ollama 地址">
          <el-input 
            v-model="localSettings.ollamaBaseUrl" 
            placeholder="http://localhost:11434" 
          />
          <div style="font-size: 12px; color: #999; margin-top: 4px;">
            Ollama 服务地址，默认为 http://localhost:11434
          </div>
        </el-form-item>
        
        <el-form-item label="本地模型">
          <el-select 
            v-model="localSettings.currentModel" 
            style="width: 100%" 
            filterable
          >
            <el-option
              v-for="model in localSettings.availableModels"
              :key="model.name"
              :label="model.name"
              :value="model.name"
            />
          </el-select>
          <div style="margin-top: 8px;">
            <el-button size="small" @click="$emit('loadModels')">
              刷新模型列表
            </el-button>
          </div>
        </el-form-item>
      </template>
      
      <!-- 远程 API 设置 -->
      <template v-else>
        <el-form-item label="AI 模型">
          <el-select v-model="localSettings.remoteModel" style="width: 100%">
            <el-option
              label="DeepSeek-R1-0528-Qwen3-8B"
              value="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
            />
            <el-option
              label="Qwen2.5-72B-Instruct"
              value="Qwen/Qwen2.5-72B-Instruct"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API Key">
          <el-input 
            v-model="localSettings.apiKey" 
            type="password" 
            show-password 
          />
        </el-form-item>
      </template>
      
      <!-- 通用设置 -->
      <el-form-item label="温度">
        <el-slider 
          v-model="localSettings.temperature" 
          :min="0" 
          :max="2" 
          :step="0.1" 
          show-tooltip 
        />
        <div style="font-size: 12px; color: #999; margin-top: 4px;">
          控制回答的创造性
        </div>
      </el-form-item>
      
      <el-form-item label="最大长度">
        <el-input-number 
          v-model="localSettings.maxTokens" 
          :min="100" 
          :max="4000" 
          :step="100" 
        />
      </el-form-item>

      <!-- 知识库设置 -->
      <el-form-item label="知识库启用">
        <el-switch 
          v-model="localSettings.useKnowledgeBase" 
          active-text="启用" 
          inactive-text="禁用" 
        />
      </el-form-item>

      <el-form-item v-if="localSettings.useKnowledgeBase" label="知识库 API 地址">
        <el-input 
          v-model="localSettings.knowledgeBaseUrl" 
          placeholder="/api/knowledge" 
        />
        <div style="font-size: 12px; color: #999; margin-top: 4px;">
          知识库服务地址，默认为 /api/knowledge
        </div>
      </el-form-item>
      
      <!-- 新增：知识库选择下拉框 -->
      <el-form-item label="知识库" v-if="localSettings.useKnowledgeBase">
        <el-select 
          v-model="localSettings.knowledgeBaseCollection" 
          placeholder="请选择知识库"
          style="width: 100%;"
          @visible-change="handleDropdownVisibleChange"
        >
          <el-option
            v-for="kb in localSettings.availableKnowledgeBases"
            :key="kb"
            :label="kb"
            :value="kb"
          />
          <template #empty>
            <div style="padding: 10px; text-align: center; color: #999;">
              没有可用的知识库，请检查后端服务。
            </div>
          </template>
        </el-select>
      </el-form-item>

      <el-form-item v-if="localSettings.useKnowledgeBase" label="最大上下文长度">
        <el-input-number 
          v-model="localSettings.maxContextLength" 
          :min="500" 
          :max="8000" 
          :step="100" 
        />
      </el-form-item>
      
      <el-form-item v-if="localSettings.useKnowledgeBase" label="检索返回文档数量">
        <el-input-number 
          v-model="localSettings.searchTopK" 
          :min="1" 
          :max="100" 
          :step="1" 
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="localShowSettings = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存设置</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  showSettings: {
    type: Boolean,
    required: true
  },
  settings: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:showSettings', 'saveSettings', 'loadModels', 'loadKnowledgeBases'])

// 本地状态
const localShowSettings = ref(props.showSettings)
const localSettings = ref({ ...props.settings })

// 监听 props 变化
watch(() => props.showSettings, (newVal) => {
  localShowSettings.value = newVal
})

watch(() => props.settings, (newVal) => {
  localSettings.value = { ...newVal }
}, { deep: true })

// 监听本地变化并同步到父组件
watch(localShowSettings, (newVal) => {
  emit('update:showSettings', newVal)
})

// 保存设置
function handleSave() {
  emit('saveSettings', localSettings.value)
  localShowSettings.value = false
}

// 新增：处理下拉框显示/隐藏事件
const handleDropdownVisibleChange = (visible) => {
  // 当下拉框即将显示时，触发事件重新加载知识库列表
  if (visible) {
    emit('loadKnowledgeBases')
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
