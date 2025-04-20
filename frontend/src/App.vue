<template>
  <div>
    <input type="file" @change="handleFileUpload" accept="image/*" />

    <div v-if="previewUrl">
      <h4>Vista previa:</h4>
      <img :src="previewUrl" alt="Vista previa" style="max-width: 300px;" />
    </div>

    <button @click="submitImage">Subir Imagen</button>

    <div v-if="uploadedImageUrl" style="margin-top: 20px;">
      <h4>Imagen:</h4>
      <img :src="uploadedImageUrl" alt="Imagen subida" style="max-width: 300px;" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const selectedFile = ref(null)
const previewUrl = ref(null)
const uploadedImageUrl = ref(null)

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  selectedFile.value = file

  if (file) {
    previewUrl.value = URL.createObjectURL(file)
  } else {
    previewUrl.value = null
  }
}

const submitImage = async () => {
  if (!selectedFile.value) {
    alert('Selecciona una imagen primero.')
    return
  }

  const formData = new FormData()
  formData.append('image', selectedFile.value)

  try {
    const response = await axios.post('http://localhost:5000/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    const filename = response.data.filename
    uploadedImageUrl.value = `http://localhost:5000/images/${filename}`
    previewUrl.value = null // Ocultamos la vista previa local
  } catch (error) {
    console.error('Error al subir la imagen:', error)
    if (error.response) {
    console.error('Respuesta del servidor:', error.response.data)
    alert(`Error del servidor: ${error.response.data.error || 'Error desconocido'}`)
  } else if (error.request) {
    console.error('No hubo respuesta del servidor')
    alert('No hubo respuesta del servidor. ¿Está corriendo el backend en http://localhost:5000?')
  } else {
    console.error('Error en la configuración de la solicitud:', error.message)
    alert('Error en la solicitud.')
  }
  }
}
</script>
