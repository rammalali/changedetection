<template>
  <div class="app-container">
    <header class="header">
      <h1>🌍 Satellite Change Detection</h1>
      <p>Upload satellite images to detect changes between two time periods</p>
    </header>

    <main class="main-content">
      <!-- Upload Section -->
      <section class="upload-section">
        <div class="upload-container">
          <div class="upload-box">
            <h3>First Image Set (Before)</h3>
            <div 
              class="drop-zone" 
              :class="{ 'drag-over': dragOverA, 'has-files': imagesA.length > 0 }"
              @drop="handleDropA"
              @dragover.prevent="dragOverA = true"
              @dragleave="dragOverA = false"
              @click="triggerFileInputA"
            >
              <input 
                ref="fileInputA" 
                type="file" 
                multiple 
                accept="image/*" 
                @change="handleFileSelectA"
                style="display: none"
              >
              <div v-if="imagesA.length === 0" class="drop-zone-content">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p>Drop images here or click to browse</p>
                <p class="hint">Or upload a folder</p>
              </div>
              <div v-else class="file-list">
                <div v-for="(file, index) in imagesA" :key="index" class="file-item">
                  <span>{{ file.name }}</span>
                  <button @click.stop="removeFileA(index)" class="remove-btn">×</button>
                </div>
              </div>
            </div>
            <input 
              ref="folderInputA" 
              type="file" 
              webkitdirectory 
              directory 
              multiple 
              @change="handleFolderSelectA"
              style="display: none"
            >
            <button @click="triggerFolderInputA" class="folder-btn">📁 Upload Folder</button>
          </div>

          <div class="upload-box">
            <h3>Second Image Set (After)</h3>
            <div 
              class="drop-zone" 
              :class="{ 'drag-over': dragOverB, 'has-files': imagesB.length > 0 }"
              @drop="handleDropB"
              @dragover.prevent="dragOverB = true"
              @dragleave="dragOverB = false"
              @click="triggerFileInputB"
            >
              <input 
                ref="fileInputB" 
                type="file" 
                multiple 
                accept="image/*" 
                @change="handleFileSelectB"
                style="display: none"
              >
              <div v-if="imagesB.length === 0" class="drop-zone-content">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p>Drop images here or click to browse</p>
                <p class="hint">Or upload a folder</p>
              </div>
              <div v-else class="file-list">
                <div v-for="(file, index) in imagesB" :key="index" class="file-item">
                  <span>{{ file.name }}</span>
                  <button @click.stop="removeFileB(index)" class="remove-btn">×</button>
                </div>
              </div>
            </div>
            <input 
              ref="folderInputB" 
              type="file" 
              webkitdirectory 
              directory 
              multiple 
              @change="handleFolderSelectB"
              style="display: none"
            >
            <button @click="triggerFolderInputB" class="folder-btn">📁 Upload Folder</button>
          </div>
        </div>
      </section>

      <!-- Options Section -->
      <section class="options-section">
        <h2>Processing Options</h2>
        <div class="options-grid">
          <div class="option-group">
            <label>Image Size</label>
            <div class="radio-group">
              <label v-for="size in [1024, 512, 256]" :key="size" class="radio-option">
                <input 
                  type="radio" 
                  :value="size" 
                  v-model="imgSize"
                >
                <span>{{ size }}</span>
              </label>
            </div>
          </div>

          <div class="option-group">
            <label>Number of Crops per Side (n × n)</label>
            <div class="radio-group">
              <label v-for="n in [1, 2, 3]" :key="n" class="radio-option">
                <input 
                  type="radio" 
                  :value="n" 
                  v-model="cropsPerSide"
                >
                <span>{{ n }}</span>
              </label>
            </div>
          </div>

          <div class="option-group">
            <label>Number of Model Calls</label>
            <div class="radio-group">
              <label v-for="calls in [1, 2, 3]" :key="calls" class="radio-option">
                <input 
                  type="radio" 
                  :value="calls" 
                  v-model="callsNb"
                >
                <span>{{ calls }}</span>
              </label>
            </div>
          </div>

          <div class="option-group">
            <label>Crop Image</label>
            <div class="toggle-group">
              <label class="toggle-option">
                <input 
                  type="radio" 
                  :value="true" 
                  v-model="cropImage"
                >
                <span>True</span>
              </label>
              <label class="toggle-option">
                <input 
                  type="radio" 
                  :value="false" 
                  v-model="cropImage"
                >
                <span>False</span>
              </label>
            </div>
          </div>
        </div>
      </section>

      <!-- Submit Button -->
      <section class="submit-section">
        <button 
          @click="processImages" 
          :disabled="!canProcess || loading"
          class="submit-btn"
        >
          <span v-if="!loading">🚀 Process Images</span>
          <span v-else>Processing...</span>
        </button>
      </section>

      <!-- Loading Indicator -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>Processing images... This may take a few minutes.</p>
      </div>

      <!-- Results Section -->
      <section v-if="results" class="results-section">
        <h2>Results</h2>
        <div class="results-info">
          <p>✅ Processing complete! Download your results below.</p>
          <button @click="downloadResults" class="download-btn">
            📥 Download Results (ZIP)
          </button>
        </div>
      </section>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        <p>❌ {{ error }}</p>
        <button @click="error = null" class="close-btn">×</button>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'App',
  setup() {
    const imagesA = ref([])
    const imagesB = ref([])
    const dragOverA = ref(false)
    const dragOverB = ref(false)
    const fileInputA = ref(null)
    const fileInputB = ref(null)
    const folderInputA = ref(null)
    const folderInputB = ref(null)
    
    const imgSize = ref(1024)
    const cropsPerSide = ref(2)
    const callsNb = ref(2)
    const cropImage = ref(true)
    
    const loading = ref(false)
    const results = ref(null)
    const error = ref(null)

    const canProcess = computed(() => {
      return imagesA.value.length > 0 && 
             imagesB.value.length > 0 && 
             imagesA.value.length === imagesB.value.length
    })

    const triggerFileInputA = () => fileInputA.value?.click()
    const triggerFileInputB = () => fileInputB.value?.click()
    const triggerFolderInputA = () => folderInputA.value?.click()
    const triggerFolderInputB = () => folderInputB.value?.click()

    const handleFileSelectA = (e) => {
      imagesA.value = Array.from(e.target.files)
    }

    const handleFileSelectB = (e) => {
      imagesB.value = Array.from(e.target.files)
    }

    const handleFolderSelectA = (e) => {
      imagesA.value = Array.from(e.target.files)
    }

    const handleFolderSelectB = (e) => {
      imagesB.value = Array.from(e.target.files)
    }

    const handleDropA = (e) => {
      e.preventDefault()
      dragOverA.value = false
      imagesA.value = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'))
    }

    const handleDropB = (e) => {
      e.preventDefault()
      dragOverB.value = false
      imagesB.value = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'))
    }

    const removeFileA = (index) => {
      imagesA.value.splice(index, 1)
    }

    const removeFileB = (index) => {
      imagesB.value.splice(index, 1)
    }

    const processImages = async () => {
      if (!canProcess.value) {
        error.value = 'Please upload equal number of images in both sets'
        return
      }

      loading.value = true
      error.value = null
      results.value = null

      try {
        const formData = new FormData()
        
        // Add images
        imagesA.value.forEach(file => {
          formData.append('images_a', file)
        })
        imagesB.value.forEach(file => {
          formData.append('images_b', file)
        })

        // Add parameters
        formData.append('img_size', imgSize.value)
        formData.append('n', cropsPerSide.value)
        formData.append('calls_nb', callsNb.value)
        formData.append('crop_image', cropImage.value)

        const response = await fetch('/change-detection', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
          throw new Error(errorData.error || `Server error: ${response.status}`)
        }

        // Store the blob for download
        const blob = await response.blob()
        results.value = blob

      } catch (err) {
        error.value = err.message || 'Failed to process images'
        console.error('Error:', err)
      } finally {
        loading.value = false
      }
    }

    const downloadResults = () => {
      if (results.value) {
        const url = window.URL.createObjectURL(results.value)
        const a = document.createElement('a')
        a.href = url
        a.download = 'change_detection_results.zip'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    }

    return {
      imagesA,
      imagesB,
      dragOverA,
      dragOverB,
      fileInputA,
      fileInputB,
      folderInputA,
      folderInputB,
      imgSize,
      cropsPerSide,
      callsNb,
      cropImage,
      loading,
      results,
      error,
      canProcess,
      triggerFileInputA,
      triggerFileInputB,
      triggerFolderInputA,
      triggerFolderInputB,
      handleFileSelectA,
      handleFileSelectB,
      handleFolderSelectA,
      handleFolderSelectB,
      handleDropA,
      handleDropB,
      removeFileA,
      removeFileB,
      processImages,
      downloadResults
    }
  }
}
</script>

