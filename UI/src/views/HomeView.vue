<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'HomeView',
  methods: {
    getProbabilityClass(probability) {
      if (probability > 0.8) {
        return 'bg-light-green';
      } else if (probability > 0.5) {
        return 'bg-light-yellow';
      } else {
        return 'bg-light-red';
      }
    }
  }
});
</script>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import axios from 'axios'

const selectedFiles = reactive([])
const isDragging = ref(false)
const activeIndex = ref(0)
const fileInput = ref(null)
const SESSION_STORAGE_KEY = 'selectedFiles';
const SESSION_EXPIRATION = 3 * 60 * 60 * 1000;
// const SESSION_EXPIRATION = 10;

watch(selectedFiles, (newFiles) => {
  if (newFiles.length === 0) {
    activeIndex.value = 0
  } else if (activeIndex.value >= newFiles.length) {
    activeIndex.value = newFiles.length - 1
  }
})

const handleFileUpload = (event, index) => {
  const file = event.target.files[0]
  if (index === undefined) {
    addNewFile(file)
  } else {
    selectedFiles[index].file = file
    selectedFiles[index].imagePreview = URL.createObjectURL(file)
    selectedFiles[index].uploaded = false
    selectedFiles[index].prediction = ''
    selectedFiles[index].probability = ''
    selectedFiles[index].probabilityValue = 0
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragging.value = false
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    addNewFile(files[0])
  }
}

const handleNewFileSelection = (event) => {
  const file = event.target.files[0]
  if (file) {
    addNewFile(file)
  }
}

const addNewFile = (file = null) => {
  selectedFiles.push({
    file,
    imagePreview: file ? URL.createObjectURL(file) : null,
    uploaded: false,
    isScanning: false,
    isBouncing: false,
    prediction: '',
    probability: '',
    probabilityValue: 0
  })
  activeIndex.value = selectedFiles.length - 1
  saveFilesToSessionStorage();
  if (file) {
    triggerBounceAnimation(activeIndex.value);
  }
}

const triggerBounceAnimation = (index) => {
  const file = selectedFiles[index];
  file.isBouncing = true;

  setTimeout(() => {
    file.isBouncing = false;
  }, 1000);
}

const uploadImage = async (index) => {
  const selectedFile = selectedFiles[index]
  if (!selectedFile.file) {
    return
  }

  const formData = new FormData()
  console.log(selectedFile.file)
  formData.append('image', selectedFile.file)

  try {
    selectedFile.isScanning = true
    // const response = await axios.post('/api/upload', formData, {
    //   headers: {
    //     'Content-Type': 'multipart/form-data'
    //   }
    // });
    // if (response.status !== 200) {
    //   throw new Error(`HTTP error! status: ${response.status}`);
    // }

    const scanningDuration = 5000
    const scanningStart = Date.now()

    await new Promise((resolve) => setTimeout(resolve, scanningDuration))

    const elapsedTime = Date.now() - scanningStart
    if (elapsedTime < scanningDuration) {
      await new Promise((resolve) => setTimeout(resolve, scanningDuration - elapsedTime))
    }

    selectedFile.prediction = `No Breast Cancer Detected`
    selectedFile.probability = `90% probability`
    selectedFile.probabilityValue = 0.6
    // selectedFile.probabilityValue = response.probability;
    // selectedFile.prediction = response.prediction;
    // selectedFile.probability = `${response.probability}% probability`;
    selectedFile.uploaded = true
  } catch (error) {
    console.error('Error uploading image:', error)
  } finally {
    selectedFile.isScanning = false
    saveFilesToSessionStorage()
  }
}

const deleteFile = (index) => {
  selectedFiles.splice(index, 1)
  saveFilesToSessionStorage()
}

const saveFilesToSessionStorage = () => {
  sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(selectedFiles));
  sessionStorage.setItem(`${SESSION_STORAGE_KEY}_timestamp`, new Date().getTime());
  // sessionStorage.setItem('selectedFiles', JSON.stringify(selectedFiles))
}

const retrieveFilesFromSessionStorage = () => {
  const storedFiles = JSON.parse(sessionStorage.getItem(SESSION_STORAGE_KEY));
  const storedTimestamp = sessionStorage.getItem(`${SESSION_STORAGE_KEY}_timestamp`);
  const currentTimestamp = new Date().getTime();

  if (storedFiles && storedTimestamp && (currentTimestamp - parseInt(storedTimestamp, 10)) < SESSION_EXPIRATION) {
    selectedFiles.splice(0, selectedFiles.length, ...storedFiles);
  } else {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    sessionStorage.removeItem(`${SESSION_STORAGE_KEY}_timestamp`);
  }

  // const storedFiles = sessionStorage.getItem('selectedFiles')
  // if (storedFiles) {
  //   selectedFiles.splice(0, selectedFiles.length, ...JSON.parse(storedFiles))
  // }
}

onMounted(() => {
  retrieveFilesFromSessionStorage()
})

onBeforeUnmount(() => {
  saveFilesToSessionStorage()
})
</script>

<template>
    <div class="container">
      <div v-if="selectedFiles.length === 0" class="drop-zone" @dragover="handleDragOver" @dragleave="handleDragLeave"
        @drop="handleDrop" :class="{ dragging: isDragging }">
        <label for="file-input-main" class="drop-zone-label">
          <img src="../assets/add.png" alt="Add Image" />
          <p>Drag and drop an image here, or click to select a file</p>
        </label>
        <input id="file-input-main" type="file" @change="(event) => handleFileUpload(event)" accept="image/*" />
      </div>
  
      <div v-if="selectedFiles.length > 0" class="image-carousel">
        <div class="image-details" v-if="selectedFiles[activeIndex]">
          <div class="image-preview" v-if="selectedFiles[activeIndex].imagePreview">
            <div class="image-container" :class="{ scanning: selectedFiles[activeIndex].isScanning }">
              <div class="image-wrapper">
                <img class="uploaded-image" :src="selectedFiles[activeIndex].imagePreview"
                  :class="{ 'bouncing': selectedFiles[activeIndex].isBouncing }" alt="Uploaded image" />
                <div class="scan-overlay"></div>
              </div>
              <div class="scan-line" v-if="selectedFiles[activeIndex].isScanning"></div>
              <div class="image-actions">
                <label :for="'file-input-' + activeIndex" class="add-icon" v-if="!selectedFiles[activeIndex].uploaded">
                  <img src="../assets/image-editing.png" alt="Edit" />
                </label>
                <input :id="'file-input-' + activeIndex" type="file"
                  @change="(event) => handleFileUpload(event, activeIndex)" accept="image/*" style="display: none" />
                <img @click="deleteFile(activeIndex)" class="delete-icon" src="../assets/trash.png" alt="Delete" />
              </div>
            </div>
          </div>
          <div class="buttons">
            <p>
              Simply upload your mammogram and let our advanced AI tool help detect potential signs of
              breast cancer
            </p>
            <div v-if="selectedFiles[activeIndex].prediction" class="prediction-message">
              <p>{{ selectedFiles[activeIndex].prediction }}</p>
              <p :class="getProbabilityClass(selectedFiles[activeIndex].probabilityValue)"
                v-if="selectedFiles[activeIndex].probability">
                {{ selectedFiles[activeIndex].probability }}
              </p>
            </div>
            <button v-if="!selectedFiles[activeIndex].uploaded" @click="uploadImage(activeIndex)"
              :disabled="!selectedFiles[activeIndex].file" class="slide">
              Upload
            </button>
            <button v-else @click="uploadImage(activeIndex)" class="slide">Reupload</button>
          </div>
        </div>
  
        <div class="tabs">
          <div v-if="selectedFiles.length > 0" class="plus-button">
            <label for="file-input-main" class="drop-zone-label">
              <img src="../assets/add-2.png" alt="Add" />
            </label>
            <input id="file-input-main" type="file" @change="(event) => handleFileUpload(event)" accept="image/*"
              style="display: none" />
          </div>
          <button v-for="(file, index) in selectedFiles" :key="index" @click="activeIndex = index"
            :class="{ active: activeIndex === index }">
            <img :src="selectedFiles[index].imagePreview" alt="Uploaded image" style="width: 50px; height: 50px" />
          </button>
        </div>
      </div>
    </div>
  </template>