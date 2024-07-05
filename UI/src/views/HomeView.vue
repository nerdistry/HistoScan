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