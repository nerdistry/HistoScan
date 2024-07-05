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

<style>
@media (min-width: 1024px) {
  #app {
    display: flex !important;
  }

  .image-details {
    width: 800px;
    height: 800px;
  }
}

.drop-zone {
  width: 700px;
  height: 300px;
  border: 2px dashed #ccc;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
  cursor: pointer;
  transition: border 0.3s ease;
  margin-top: 10px;

  & img {
    width: 130px;
    margin-bottom: 20px;
  }
}

.drop-zone.dragging {
  border-color: #000;
}

.drop-zone input[type='file'] {
  display: none;
}

.drop-zone-label {
  cursor: pointer;
}

.drop-zone p {
  margin: 0;
  text-align: center;
}

.image-details {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  padding: 10px 5px;
  height: 350px;
  border: 1px solid #777777;
  border-radius: 10px;
}

.image-carousel {
  margin-top: 20px;
}

.image-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  width: 250px;
  height: 250px;

  & .uploaded-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
  }

  & .image-actions {
    margin-top: 20px;

    & img {
      width: 45px;
      margin: 0 5px;
      padding: 5px;
      background-color: white;
      border-radius: 10px;
      transition: all 0.3s ease-in-out;

      &:hover {
        cursor: pointer;
        opacity: 0.8;
      }
    }
  }
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.scan-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 0;
  border-radius: 20px 20px 0 0;
  background-color: #fff;
  mix-blend-mode: difference;
  pointer-events: none;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 8px;
  background: #3fefef;
  border-radius: 8px;
  filter: drop-shadow(0 0 20px #3fefef) drop-shadow(0 0 60px #3fefef);
  opacity: 0;
  z-index: 1;
}

.scanning .scan-overlay {
  animation: scan-effect 5s linear infinite;
}

.scanning .scan-line {
  animation: scan-line 5s linear infinite;
}

.bouncing {
  animation: bounce 1.4s ease;
}

.image-preview {
  display: flex;
  align-items: start;
  justify-content: start;
  margin-top: 15px;
  flex-direction: column;
  width: 100%;
  justify-self: self-start;
  border-right: 1px dashed rgb(136, 136, 136);
}

.add-icon {
  cursor: pointer;
}

.image-carousel .buttons .bg-light-green {
  background-color: #a2ffd5;
}

.image-carousel .buttons .bg-light-red {
  background-color: #ffa2a2;
}

.image-carousel .buttons .bg-light-yellow {
  background-color: #fffaa2;
}

.image-carousel .buttons {
  width: 70%;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0 15px 20px 15px;

  &>p {
    padding: 10px;
    background-color: rgba(223, 255, 238, 0.8);
    color: black;
    margin-top: 15px;
    border-radius: 10px;
  }

  & button {
    background-color: #181818;
    border: 3px solid #42b883;
    color: #42b883;
    padding: 8px 40px;
    border-radius: 30px;
    font-size: 23px;
    transition: all 0.3s ease-in-out;

    &:hover {
      cursor: pointer;
      color: black;
      background-color: #42b883;
    }
  }
}

.prediction-message {
  margin-top: 10px;
  animation: show-fade 2s ease-in-out;

  & p {
    padding: 10px;
    background-color: white;
    color: black;
    margin-top: 10px;
    margin-bottom: 10px;
    border-radius: 10px;
  }
}

.tabs {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.tabs button {
  width: 70px;
  height: 70px;
  border: transparent;
  cursor: pointer;
  border-radius: 10px;
  transition: 0.3s ease-in;

  &:hover {
    opacity: 0.8;
  }
}

.tabs .plus-button {
  width: 70px;
  height: 70px;
  border: transparent;
  background: rgba(208, 255, 230, 0.8);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: 0.3s ease-in;

  &:hover {
    opacity: 0.8;
  }

  & img {
    width: 40px;
    margin-top: 5px;
  }
}

.tabs button.active {
  transition: all 0.3s ease-in-out;
  background: rgba(66, 184, 131, 0.6);
  color: white;
}

@keyframes scan-effect {

  0%,
  100% {
    height: 0;
  }

  50% {
    height: 100%;
  }
}

@keyframes scan-line {

  0%,
  100% {
    top: 0;
    opacity: 0;
  }

  5%,
  95% {
    opacity: 1;
  }

  50% {
    top: calc(100% - 4px);
  }
}

@keyframes bounce {

  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }

  40% {
    transform: translateY(-30px);
  }

  60% {
    transform: translateY(-15px);
  }
}

@keyframes show-fade {
  0% {
    opacity: 0;
  }

  100% {
    opacity: 1;
  }
}
</style>
