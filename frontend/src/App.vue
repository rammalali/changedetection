<template>
  <div class="app-container">
    <header class="header">
      <h1>🌍  Change Detection</h1>
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
          <div class="option-card">
            <div class="option-label">
              <span class="label-text">Image Size</span>
            </div>
            <div class="option-buttons">
              <button
                v-for="size in [1024, 512, 256]"
                :key="size"
                type="button"
                :class="['option-btn', { active: imgSize === size }]"
                @click="imgSize = size"
              >
                {{ size }}
              </button>
            </div>
          </div>

          <div class="option-card">
            <div class="option-label">
              <span class="label-text">Number of Crops per Side (n × n)</span>
            </div>
            <div class="option-buttons">
              <button
                v-for="n in [1, 2, 3]"
                :key="n"
                type="button"
                :class="['option-btn', { active: cropsPerSide === n }]"
                @click="cropsPerSide = n"
              >
                {{ n }}
              </button>
            </div>
          </div>

          <div class="option-card">
            <div class="option-label">
              <span class="label-text">Number of Model Calls</span>
            </div>
            <div class="option-buttons">
              <button
                v-for="calls in [1, 2, 3]"
                :key="calls"
                type="button"
                :class="['option-btn', { active: callsNb === calls }]"
                @click="callsNb = calls"
              >
                {{ calls }}
              </button>
            </div>
          </div>

          <div class="option-card">
            <div class="option-label">
              <span class="label-text">Crop Image</span>
            </div>
            <div class="option-buttons">
              <button
                type="button"
                :class="['option-btn', { active: cropImage === true }]"
                @click="cropImage = true"
              >
                True
              </button>
              <button
                type="button"
                :class="['option-btn', { active: cropImage === false }]"
                @click="cropImage = false"
              >
                False
              </button>
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
      <section v-if="results && results.length > 0" class="results-section">
        <h2>Results</h2>
        <p class="results-success">✅ Processing complete! View your results below.</p>
        
        <div v-for="(result, index) in results" :key="index" class="result-item">
          <h3>{{ result.filename }}</h3>
          <div class="results-grid">
            <div v-if="result.mask" class="result-image-card">
              <h4>Mask</h4>
              <img :src="`data:image/png;base64,${result.mask}`" alt="Mask" class="result-image">
              <a :href="`data:image/png;base64,${result.mask}`" :download="`${result.filename}_mask.png`" class="download-image-btn">
                📥 Download
              </a>
            </div>
            <div v-if="result.color_mask" class="result-image-card">
              <h4>Color Mask</h4>
              <img :src="`data:image/png;base64,${result.color_mask}`" alt="Color Mask" class="result-image">
              <a :href="`data:image/png;base64,${result.color_mask}`" :download="`${result.filename}_color_mask.png`" class="download-image-btn">
                📥 Download
              </a>
            </div>
            <div v-if="result.overlay_a" class="result-image-card">
              <h4>Overlay A (Before)</h4>
              <img :src="`data:image/png;base64,${result.overlay_a}`" alt="Overlay A" class="result-image">
              <a :href="`data:image/png;base64,${result.overlay_a}`" :download="`${result.filename}_overlay_a.png`" class="download-image-btn">
                📥 Download
              </a>
            </div>
            <div v-if="result.overlay_b" class="result-image-card">
              <h4>Overlay B (After)</h4>
              <img :src="`data:image/png;base64,${result.overlay_b}`" alt="Overlay B" class="result-image">
              <a :href="`data:image/png;base64,${result.overlay_b}`" :download="`${result.filename}_overlay_b.png`" class="download-image-btn">
                📥 Download
              </a>
            </div>
          </div>
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

        // Get JSON response with base64 encoded images
        const data = await response.json()
        results.value = data.results || []

      } catch (err) {
        error.value = err.message || 'Failed to process images'
        console.error('Error:', err)
      } finally {
        loading.value = false
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
      processImages
    }
  }
}
</script>

