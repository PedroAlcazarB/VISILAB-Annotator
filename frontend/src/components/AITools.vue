<template>
  <div class="ai-tools">
    <h3>
      <i class="fas fa-robot"></i>
      Herramientas de IA
    </h3>
    
    <!-- Sección de carga de modelo -->
    <div class="ai-section">
      <h4>Modelo de IA</h4>
      
      <!-- Desplegable para modelos guardados -->
      <div v-if="savedModels.length > 0" class="form-group">
        <label for="saved-models">Modelos guardados:</label>
        <select 
          id="saved-models"
          v-model="selectedSavedModel" 
          class="form-control"
          :disabled="isModelLoaded"
          @change="loadSavedModel"
        >
          <option value="">Seleccionar modelo guardado...</option>
          <option 
            v-for="model in savedModels" 
            :key="model.id" 
            :value="model.id"
          >
            {{ model.name }} ({{ model.categories.length }} categorías)
          </option>
        </select>
      </div>
      
      <div v-if="savedModels.length > 0" class="separator">
        <span>O cargar nuevo modelo</span>
      </div>
      
      <!-- Input para el nombre del modelo -->
      <div class="form-group">
        <label for="model-name">Nombre del modelo:</label>
        <input 
          id="model-name"
          v-model="modelName" 
          type="text" 
          class="form-control"
          placeholder="Ej: Detector de armas v1.0"
          :disabled="isModelLoaded"
        />
      </div>
      
      <!-- Input para cargar archivo del modelo -->
      <div class="form-group">
        <label for="model-file">Cargar modelo (.pt):</label>
        <input 
          id="model-file"
          ref="modelFileInput"
          type="file" 
          accept=".pt"
          class="form-control file-input"
          @change="handleModelFileSelect"
          :disabled="isModelLoaded || isLoadingModel"
        />
      </div>
      
      <!-- Input para cargar archivo YAML (opcional) -->
      <div class="form-group">
        <label for="yaml-file">Archivo de configuración (.yaml - opcional):</label>
        <input 
          id="yaml-file"
          ref="yamlFileInput"
          type="file" 
          accept=".yaml,.yml"
          class="form-control file-input"
          @change="handleYamlFileSelect"
          :disabled="isModelLoaded || isLoadingModel"
        />
      </div>
      
      <!-- Botón para cargar modelo -->
      <button 
        @click="loadModel"
        class="btn btn-primary"
        :disabled="!canLoadModel || isLoadingModel"
      >
        <i v-if="isLoadingModel" class="fas fa-spinner fa-spin"></i>
        <i v-else class="fas fa-upload"></i>
        {{ isLoadingModel ? 'Cargando...' : 'Cargar Modelo' }}
      </button>
      
      <!-- Estado del modelo -->
      <div v-if="isModelLoaded" class="model-status loaded">
        <i class="fas fa-check-circle"></i>
        <div class="status-info">
          <strong>{{ loadedModelName }}</strong>
          <span>Modelo cargado exitosamente</span>
        </div>
        <button @click="unloadModel" class="btn btn-sm btn-outline" title="Descargar modelo">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div v-else-if="modelError" class="model-status error">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ modelError }}</span>
      </div>
    </div>
    
    <!-- Sección de categorías del modelo -->
    <div v-if="isModelLoaded && modelCategories.length > 0" class="ai-section">
      <h4>Categorías del Modelo</h4>
      <div class="categories-list">
        <div 
          v-for="(category, index) in modelCategories" 
          :key="index"
          class="category-item"
        >
          <span class="category-index">{{ index }}</span>
          <span class="category-name">{{ category }}</span>
        </div>
      </div>
    </div>
    
    <!-- Sección de predicción -->
    <div class="ai-section">
      <h4>Predicción</h4>
      
      <!-- Configuración de confianza -->
      <div class="form-group">
        <label for="confidence">
          Umbral de confianza: {{ confidence }}
          <i class="fas fa-info-circle" title="Determina qué tan seguro debe estar el modelo para mostrar una detección. 0.1 = muy permisivo, 0.8 = muy estricto"></i>
        </label>
        <input 
          id="confidence"
          v-model.number="confidence"
          type="range"
          min="0.1"
          max="1.0"
          step="0.05"
          class="form-control range-input"
          :disabled="!isModelLoaded"
        />
        <div class="confidence-guide">
          <small>
            <strong>Guía:</strong>
            0.1-0.3 (Permisivo) | 0.4-0.6 (Equilibrado) | 0.7-1.0 (Estricto)
          </small>
        </div>
      </div>
      
      <!-- Botón de predicción -->
      <button 
        @click="predictImage"
        class="btn btn-success"
        :disabled="!canPredict || isPredicting"
      >
        <i v-if="isPredicting" class="fas fa-spinner fa-spin"></i>
        <i v-else class="fas fa-magic"></i>
        {{ isPredicting ? 'Prediciendo...' : 'Predecir Imagen' }}
      </button>
      
      <!-- Botón para limpiar predicciones -->
      <button 
        v-if="lastPrediction"
        @click="clearPredictions"
        class="btn btn-outline"
      >
        <i class="fas fa-eraser"></i>
        Limpiar Predicciones
      </button>
      
      <!-- Resultados de predicción -->
      <div v-if="lastPrediction" class="prediction-results">
        <h5>Últimos resultados:</h5>
        <div v-if="lastPrediction.detections && lastPrediction.detections.length > 0">
          <p><strong>{{ lastPrediction.detections.length }}</strong> detecciones encontradas</p>
          <div class="detections-summary">
            <div 
              v-for="detection in lastPrediction.detections.slice(0, 5)" 
              :key="`${detection.bbox[0]}-${detection.bbox[1]}`"
              class="detection-item"
            >
              <span class="detection-class">{{ getClassName(detection.class) }}</span>
              <span class="detection-confidence">{{ (detection.confidence * 100).toFixed(1) }}%</span>
            </div>
            <div v-if="lastPrediction.detections.length > 5" class="more-detections">
              +{{ lastPrediction.detections.length - 5 }} más...
            </div>
          </div>
        </div>
        <div v-else>
          <p>No se encontraron detecciones</p>
        </div>
      </div>
    </div>
    
    <!-- Navegación entre imágenes -->
    <div v-if="isModelLoaded" class="ai-section">
      <h4>Navegación</h4>
      <div class="navigation-controls">
        <button 
          @click="goToPreviousImage"
          class="btn btn-outline"
          :disabled="!canNavigatePrevious"
        >
          <i class="fas fa-chevron-left"></i>
          Anterior
        </button>
        
        <button 
          @click="goToNextImage"
          class="btn btn-outline"
          :disabled="!canNavigateNext"
        >
          Siguiente
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
      
      <div class="auto-predict">
        <label>
          <input 
            v-model="autoPredictOnNavigate" 
            type="checkbox"
          />
          Predecir automáticamente al cambiar imagen
        </label>
      </div>
    </div>

  </div>
</template>

<script>
import { useAnnotationStore } from '../stores/annotationStore'

export default {
  name: 'AITools',
  props: {
    currentImage: {
      type: Object,
      default: null
    },
    datasetId: {
      type: String,
      required: true
    }
  },
  setup() {
    const store = useAnnotationStore()
    return { store }
  },
  data() {
    return {
      // Estado del modelo
      modelName: '',
      loadedModelName: '',
      selectedModelFile: null,
      selectedYamlFile: null,
      isModelLoaded: false,
      isLoadingModel: false,
      modelError: null,
      modelCategories: [],
      
      // Modelos guardados
      savedModels: [],
      selectedSavedModel: '',
      isLoadingSavedModels: false,
      
      // Configuración de predicción
      confidence: 0.5,
      isPredicting: false,
      lastPrediction: null,
      
      // Navegación
      autoPredictOnNavigate: true
    }
  },
  computed: {
    canLoadModel() {
      return this.modelName.trim() && this.selectedModelFile && !this.isModelLoaded
    },
    
    canPredict() {
      return this.isModelLoaded && this.currentImage && !this.isPredicting
    },
    
    canNavigatePrevious() {
      if (!this.currentImage) return false
      const images = this.store.images
      const currentIndex = images.findIndex(img => img._id === this.currentImage._id)
      return currentIndex > 0
    },
    
    canNavigateNext() {
      if (!this.currentImage) return false
      const images = this.store.images
      const currentIndex = images.findIndex(img => img._id === this.currentImage._id)
      return currentIndex < images.length - 1
    }
  },
  watch: {
    currentImage: {
      handler(newImage, oldImage) {
        if (newImage && oldImage && newImage._id !== oldImage._id) {
          if (this.autoPredictOnNavigate && this.isModelLoaded) {
            // Pequeño delay para asegurar que la imagen se haya cargado
            setTimeout(() => {
              this.predictImage()
            }, 500)
          } else {
            // Si la predicción automática está deshabilitada, limpiar predicciones anteriores
            this.lastPrediction = null
          }
        }
      },
      immediate: false
    }
  },
  
  async mounted() {
    await this.loadSavedModelsList()
  },
  
  methods: {
    async loadSavedModelsList() {
      this.isLoadingSavedModels = true
      try {
        const response = await fetch('http://localhost:5000/api/ai/saved-models')
        const result = await response.json()
        
        if (response.ok) {
          this.savedModels = result.models || []
        } else {
          console.error('Error al cargar modelos guardados:', result.error)
        }
      } catch (error) {
        console.error('Error de conexión al cargar modelos:', error)
      } finally {
        this.isLoadingSavedModels = false
      }
    },
    
    async loadSavedModel() {
      if (!this.selectedSavedModel) return
      
      this.isLoadingModel = true
      this.modelError = null
      
      try {
        const response = await fetch('http://localhost:5000/api/ai/load-saved-model', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model_id: this.selectedSavedModel,
            dataset_id: this.datasetId
          })
        })
        
        const result = await response.json()
        
        if (response.ok) {
          this.isModelLoaded = true
          this.loadedModelName = result.model_info.name
          this.modelCategories = result.categories || []
          
          // Si se crearon categorías, recargar las categorías del store
          if (result.created_categories && result.created_categories.length > 0) {
            await this.store.loadCategories(this.datasetId)
            console.log(`Se crearon ${result.created_categories.length} categorías automáticamente`)
          }
          
          this.$emit('model-loaded', {
            name: this.loadedModelName,
            categories: this.modelCategories
          })
        } else {
          this.modelError = result.error || 'Error al cargar el modelo guardado'
        }
      } catch (error) {
        console.error('Error loading saved model:', error)
        this.modelError = 'Error de conexión al cargar el modelo guardado'
      } finally {
        this.isLoadingModel = false
      }
    },
    handleModelFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.selectedModelFile = file
        // Si no hay nombre del modelo, usar el nombre del archivo sin extensión
        if (!this.modelName.trim()) {
          this.modelName = file.name.replace(/\.[^/.]+$/, "")
        }
      }
    },
    
    handleYamlFileSelect(event) {
      const file = event.target.files[0]
      this.selectedYamlFile = file
    },
    
    async loadModel() {
      if (!this.canLoadModel) return
      
      this.isLoadingModel = true
      this.modelError = null
      
      try {
        const formData = new FormData()
        formData.append('model_file', this.selectedModelFile)
        formData.append('model_name', this.modelName)
        formData.append('dataset_id', this.datasetId)
        
        if (this.selectedYamlFile) {
          formData.append('yaml_file', this.selectedYamlFile)
        }
        
        const response = await fetch('http://localhost:5000/api/ai/load-model', {
          method: 'POST',
          body: formData
        })
        
        const result = await response.json()
        
        if (response.ok) {
          this.isModelLoaded = true
          this.loadedModelName = this.modelName
          this.modelCategories = result.categories || []
          
          // Si se crearon categorías, recargar las categorías del store
          if (result.created_categories && result.created_categories.length > 0) {
            await this.store.loadCategories(this.datasetId)
            console.log(`Se crearon ${result.created_categories.length} categorías automáticamente`)
          }
          
          // Limpiar inputs
          this.$refs.modelFileInput.value = ''
          this.$refs.yamlFileInput.value = ''
          this.selectedModelFile = null
          this.selectedYamlFile = null
          
          // Actualizar lista de modelos guardados
          await this.loadSavedModelsList()
          
          this.$emit('model-loaded', {
            name: this.loadedModelName,
            categories: this.modelCategories
          })
        } else {
          this.modelError = result.error || 'Error al cargar el modelo'
        }
      } catch (error) {
        console.error('Error loading model:', error)
        this.modelError = 'Error de conexión al cargar el modelo'
      } finally {
        this.isLoadingModel = false
      }
    },
    
    async unloadModel() {
      try {
        const response = await fetch('http://localhost:5000/api/ai/unload-model', {
          method: 'POST'
        })
        
        if (response.ok) {
          this.isModelLoaded = false
          this.loadedModelName = ''
          this.modelCategories = []
          this.lastPrediction = null
          this.modelName = ''
          this.selectedSavedModel = ''  // Limpiar selección del desplegable
          
          // Las anotaciones se manejan automáticamente por el store
          
          this.$emit('model-unloaded')
        }
      } catch (error) {
        console.error('Error unloading model:', error)
      }
    },
    
    async predictImage() {
      if (!this.canPredict) return
      
      this.isPredicting = true
      
      try {
        const response = await fetch('http://localhost:5000/api/ai/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            image_id: this.currentImage._id,
            confidence: this.confidence
          })
        })
        
        const result = await response.json()
        
        if (response.ok) {
          this.lastPrediction = result
          
          // Las predicciones ahora se guardan automáticamente como anotaciones en el backend
          // Solo necesitamos notificar que se crearon nuevas anotaciones
          const detectionCount = result.detections ? result.detections.length : 0
          const annotationsCreated = result.annotations ? result.annotations.length : 0
          
          // Emitir evento para refrescar las anotaciones en el canvas
          this.$emit('annotations-updated', {
            annotations: result.annotations || [],
            created_categories: result.created_categories || [],
            message: result.message || `Se crearon ${annotationsCreated} anotaciones de ${detectionCount} detecciones.`
          })
          
          // Log para depuración
          console.log(`Predicción completada: ${detectionCount} detecciones encontradas, ${annotationsCreated} anotaciones creadas automáticamente`)
          
          // Mostrar mensaje informativo si se crearon categorías
          if (result.created_categories && result.created_categories.length > 0) {
            const categoryNames = result.created_categories.map(cat => cat.name).join(', ')
            console.log(`Se crearon automáticamente las categorías: ${categoryNames}`)
          }
          
        } else {
          console.error('Prediction error:', result.error)
          
          // Mostrar error más detallado
          let errorMessage = 'Error en la predicción'
          if (result.error) {
            if (result.error.includes('bytes-like object is required')) {
              errorMessage = 'Error de formato de imagen. La imagen puede estar corrupta.'
            } else if (result.error.includes('No hay modelo cargado')) {
              errorMessage = 'No hay modelo cargado. Por favor, carga un modelo primero.'
            } else if (result.error.includes('No se pueden crear anotaciones sin categorías')) {
              errorMessage = 'No hay categorías disponibles. Las categorías del modelo se crearán automáticamente en la primera predicción.'
            } else {
              errorMessage = result.error
            }
          }
          
          alert(errorMessage)
        }
      } catch (error) {
        console.error('Error predicting image:', error)
        alert('Error de conexión durante la predicción. Verifica que el servidor esté funcionando.')
      } finally {
        this.isPredicting = false
      }
    },
    
    getClassName(classIndex) {
      return this.modelCategories[classIndex] || `Clase ${classIndex}`
    },
    
    goToPreviousImage() {
      if (!this.canNavigatePrevious) return
      
      const images = this.store.images
      const currentIndex = images.findIndex(img => img._id === this.currentImage._id)
      const previousImage = images[currentIndex - 1]
      
      this.$emit('navigate-to-image', previousImage)
    },
    
    goToNextImage() {
      if (!this.canNavigateNext) return
      
      const images = this.store.images
      const currentIndex = images.findIndex(img => img._id === this.currentImage._id)
      const nextImage = images[currentIndex + 1]
      
      this.$emit('navigate-to-image', nextImage)
    },
    
    clearPredictions() {
      this.lastPrediction = null
      // Las anotaciones se manejan automáticamente
    }
  }
}
</script>

<style scoped>
.ai-tools {
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.ai-tools h3 {
  background: #f8f9fa;
  margin: 0;
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
  color: #495057;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-tools h3 i {
  color: #6f42c1;
}

.ai-section {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.ai-section:last-child {
  border-bottom: none;
}

.ai-section h4 {
  margin: 0 0 15px 0;
  color: #343a40;
  font-size: 0.95rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
}

.form-group label i {
  margin-left: 5px;
  color: #6c757d;
  cursor: help;
}

.confidence-guide {
  margin-top: 5px;
  text-align: center;
}

.confidence-guide small {
  color: #6c757d;
  font-size: 0.8rem;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control:disabled {
  background-color: #e9ecef;
  opacity: 1;
}

.file-input {
  padding: 6px 8px;
}

.range-input {
  padding: 0;
  height: 30px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #1e7e34;
}

.btn-outline {
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline:hover:not(:disabled) {
  background-color: #6c757d;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.8rem;
}

.model-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  font-size: 0.9rem;
}

.model-status.loaded {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.model-status.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.status-info strong {
  margin-bottom: 2px;
}

.status-info span {
  font-size: 0.8rem;
  opacity: 0.8;
}

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 150px;
  overflow-y: auto;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.category-index {
  background-color: #6c757d;
  color: white;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  min-width: 24px;
  text-align: center;
}

.category-name {
  font-weight: 500;
  color: #495057;
}

.prediction-results {
  margin-top: 15px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.prediction-results h5 {
  margin: 0 0 10px 0;
  color: #495057;
  font-size: 0.9rem;
}

.detections-summary {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background-color: white;
  border-radius: 3px;
  border: 1px solid #dee2e6;
  font-size: 0.85rem;
}

.detection-class {
  font-weight: 500;
  color: #495057;
}

.detection-confidence {
  color: #28a745;
  font-weight: 600;
}

.more-detections {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  font-size: 0.8rem;
  padding: 4px;
}

.navigation-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.navigation-controls .btn {
  flex: 1;
  justify-content: center;
}

.auto-predict {
  margin-top: 10px;
}

.auto-predict label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #495057;
  cursor: pointer;
  font-weight: normal;
}

.auto-predict input[type="checkbox"] {
  margin: 0;
}

/* Estilos para la sección de ayuda */
.help-section {
  border: 2px solid #e3f2fd;
  border-radius: 8px;
  background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%);
  margin-top: 15px;
}

.help-section h4 {
  color: #1976d2;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.help-content {
  font-size: 0.85rem;
}

.help-content p {
  margin: 0 0 10px 0;
  color: #424242;
  font-weight: 500;
}

.help-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 4px;
  color: #424242;
}

.help-item i {
  width: 16px;
  text-align: center;
}

.help-item strong {
  min-width: 60px;
}

.help-note {
  margin-top: 12px;
  padding: 8px;
  background: rgba(25, 118, 210, 0.1);
  border-radius: 4px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.help-note i {
  color: #1976d2;
  margin-top: 2px;
}

.help-note small {
  color: #424242;
  line-height: 1.3;
}

.text-success {
  color: #28a745 !important;
}

.text-danger {
  color: #dc3545 !important;
}

/* Estilos para el separador */
.separator {
  margin: 15px 0;
  text-align: center;
  position: relative;
}

.separator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #dee2e6;
}

.separator span {
  background: white;
  padding: 0 10px;
  color: #6c757d;
  font-size: 0.85rem;
  position: relative;
  z-index: 1;
}
</style>