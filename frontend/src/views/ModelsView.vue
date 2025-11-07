<template>
  <div class="models-view">
    <div class="models-container">
      <h1>Gestión de Modelos de IA</h1>
      <p class="subtitle">Administra los modelos de detección para usar en el anotador</p>

      <!-- Botón para añadir modelo personalizado -->
      <div class="actions-bar">
        <button @click="showUploadModal = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Añadir Modelo Personalizado
        </button>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando modelos...</p>
      </div>

      <!-- Todos los modelos en una sola sección -->
      <div v-else class="models-sections">
        <section class="models-section">
          <h2>Modelos de IA</h2>
          <p class="section-description">Explora y administra los modelos precargados y personalizados disponibles.</p>
          
          <div v-if="allModels.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>No hay modelos disponibles</p>
          </div>
          
          <div v-else class="models-grid">
            <div 
              v-for="model in allModels" 
              :key="model.id"
              class="model-card"
              :class="{ 'preloaded': model.is_preloaded, 'custom': !model.is_preloaded }"
            >
              <div class="model-header">
                <div class="model-badge" :class="{ 'preloaded': model.is_preloaded, 'custom': !model.is_preloaded }">
                  <i :class="model.is_preloaded ? 'fas fa-star' : 'fas fa-user'"></i>
                  {{ model.is_preloaded ? 'Precargado' : 'Personalizado' }}
                </div>
              </div>
              <div class="model-body">
                <h3>{{ model.name }}</h3>
                <p class="model-description">{{ model.description || 'Sin descripción' }}</p>
                <div class="model-stats">
                  <span><i class="fas fa-tags"></i> {{ model.categories?.length || 0 }} categorías</span>
                  <span><i class="fas fa-file"></i> {{ formatFileSize(model.file_size) }}</span>
                </div>
                <div class="model-categories">
                  <span 
                    v-for="(cat, idx) in (model.categories || []).slice(0, 3)" 
                    :key="idx"
                    class="category-tag"
                  >
                    {{ cat }}
                  </span>
                  <span v-if="model.categories && model.categories.length > 3" class="category-tag more">
                    +{{ model.categories.length - 3 }}
                  </span>
                </div>
              </div>
              <!-- Solo mostrar botón de eliminar para modelos personalizados -->
              <div v-if="!model.is_preloaded" class="model-actions">
                <button 
                  @click="deleteModel(model)" 
                  class="btn btn-danger"
                  title="Eliminar modelo"
                >
                  <i class="fas fa-trash"></i>
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Modal para subir modelo -->
    <div v-if="showUploadModal" class="modal-overlay" @click="closeUploadModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2><i class="fas fa-upload"></i> Subir Modelo Personalizado</h2>
          <button @click="closeUploadModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="uploadModel" class="upload-form">
            <!-- Nombre del modelo -->
            <div class="form-group">
              <label for="model-name">Nombre del modelo: *</label>
              <input 
                id="model-name"
                v-model="newModel.name" 
                type="text" 
                class="form-control"
                placeholder="Ej: Detector de vehículos v2.0"
                required
              />
            </div>

            <!-- Descripción -->
            <div class="form-group">
              <label for="model-description">Descripción (opcional):</label>
              <textarea 
                id="model-description"
                v-model="newModel.description" 
                class="form-control"
                placeholder="Describe para qué sirve este modelo..."
                rows="3"
              ></textarea>
            </div>
            
            <!-- Archivo del modelo -->
            <div class="form-group">
              <label for="model-file">Archivo del modelo (.pt): *</label>
              <input 
                id="model-file"
                ref="modelFileInput"
                type="file" 
                accept=".pt"
                class="form-control file-input"
                @change="handleModelFileSelect"
                required
              />
              <small class="form-help">Selecciona un archivo de modelo YOLO (.pt)</small>
            </div>
            
            <!-- Archivo YAML -->
            <div class="form-group">
              <label for="yaml-file">Archivo de configuración (.yaml - opcional):</label>
              <input 
                id="yaml-file"
                ref="yamlFileInput"
                type="file" 
                accept=".yaml,.yml"
                class="form-control file-input"
                @change="handleYamlFileSelect"
              />
              <small class="form-help">Archivo YAML con las categorías del modelo</small>
            </div>

            <!-- Mensajes de error -->
            <div v-if="uploadError" class="alert alert-error">
              <i class="fas fa-exclamation-circle"></i>
              {{ uploadError }}
            </div>

            <!-- Mensajes de éxito -->
            <div v-if="uploadSuccess" class="alert alert-success">
              <i class="fas fa-check-circle"></i>
              {{ uploadSuccess }}
            </div>

            <!-- Botones -->
            <div class="form-actions">
              <button 
                type="button" 
                @click="closeUploadModal" 
                class="btn btn-secondary"
                :disabled="uploading"
              >
                Cancelar
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="uploading || !canUpload"
              >
                <i v-if="uploading" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-upload"></i>
                {{ uploading ? 'Subiendo...' : 'Subir Modelo' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelsView',
  data() {
    return {
      loading: false,
      preloadedModels: [],
      customModels: [],
      showUploadModal: false,
      uploading: false,
      uploadError: null,
      uploadSuccess: null,
      newModel: {
        name: '',
        description: '',
        file: null,
        yamlFile: null
      }
    }
  },
  computed: {
    canUpload() {
      return this.newModel.name.trim() && this.newModel.file
    },
    allModels() {
      // Combinar modelos precargados y personalizados en una sola lista
      const all = [...this.preloadedModels, ...this.customModels]
      return all.sort((a, b) => {
        // Ordenar por tipo (precargados primero) y luego por nombre
        if (a.is_preloaded && !b.is_preloaded) return -1
        if (!a.is_preloaded && b.is_preloaded) return 1
        return (a.name || '').localeCompare(b.name || '')
      })
    }
  },
  async mounted() {
    await this.loadModels()
  },
  methods: {
    async loadModels() {
      this.loading = true
      try {
        const response = await fetch('http://localhost:5000/api/ai/saved-models')
        const result = await response.json()
        
        if (response.ok) {
          this.preloadedModels = result.preloaded || []
          this.customModels = result.custom || []
        } else {
          console.error('Error al cargar modelos:', result.error)
        }
      } catch (error) {
        console.error('Error de conexión:', error)
      } finally {
        this.loading = false
      }
    },

    handleModelFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.newModel.file = file
        // Si no hay nombre, usar el nombre del archivo
        if (!this.newModel.name.trim()) {
          this.newModel.name = file.name.replace(/\.[^/.]+$/, "")
        }
      }
    },

    handleYamlFileSelect(event) {
      this.newModel.yamlFile = event.target.files[0]
    },

    async uploadModel() {
      if (!this.canUpload) return
      
      this.uploading = true
      this.uploadError = null
      this.uploadSuccess = null
      
      try {
        const formData = new FormData()
        formData.append('model_file', this.newModel.file)
        formData.append('model_name', this.newModel.name)
        formData.append('description', this.newModel.description)
        
        if (this.newModel.yamlFile) {
          formData.append('yaml_file', this.newModel.yamlFile)
        }
        
        const response = await fetch('http://localhost:5000/api/ai/load-model', {
          method: 'POST',
          body: formData
        })
        
        const result = await response.json()
        
        if (response.ok) {
          this.uploadSuccess = 'Modelo subido exitosamente'
          
          // Recargar lista de modelos
          await this.loadModels()
          
          // Limpiar formulario después de un delay
          setTimeout(() => {
            this.closeUploadModal()
          }, 1500)
        } else {
          this.uploadError = result.error || 'Error al subir el modelo'
        }
      } catch (error) {
        console.error('Error uploading model:', error)
        this.uploadError = 'Error de conexión al subir el modelo'
      } finally {
        this.uploading = false
      }
    },

    async deleteModel(model) {
      if (!confirm(`¿Estás seguro de que quieres eliminar el modelo "${model.name}"?\n\nEsta acción no se puede deshacer.`)) {
        return
      }
      
      try {
        const response = await fetch(`http://localhost:5000/api/ai/models/${model.id}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          // Recargar modelos
          await this.loadModels()
        } else {
          const result = await response.json()
          alert('Error al eliminar el modelo: ' + (result.error || 'Error desconocido'))
        }
      } catch (error) {
        console.error('Error deleting model:', error)
        alert('Error de conexión al eliminar el modelo')
      }
    },

    closeUploadModal() {
      this.showUploadModal = false
      this.uploadError = null
      this.uploadSuccess = null
      this.newModel = {
        name: '',
        description: '',
        file: null,
        yamlFile: null
      }
      if (this.$refs.modelFileInput) this.$refs.modelFileInput.value = ''
      if (this.$refs.yamlFileInput) this.$refs.yamlFileInput.value = ''
    },

    formatFileSize(bytes) {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }
  }
}
</script>

<style scoped>
.models-view {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.models-container {
  max-width: 1400px;
  margin: 0 auto;
}

.models-container h1 {
  font-size: 2rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 2rem;
}

.actions-bar {
  margin-bottom: 2rem;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.models-sections {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.models-section h2 {
  font-size: 1.5rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-description {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  background: white;
  border-radius: 12px;
  border: 2px dashed #e2e8f0;
}

.empty-state i {
  font-size: 3rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #64748b;
  margin-bottom: 1rem;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.model-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.2s;
}

.model-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.model-card.preloaded {
  border-left: 4px solid #f59e0b;
}

.model-card.custom {
  border-left: 4px solid #3b82f6;
}

.model-header {
  padding: 0.75rem 1.5rem;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.model-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.model-badge.custom {
  background: #dbeafe;
  color: #1e40af;
}

.model-body {
  padding: 1.5rem;
}

.model-body h3 {
  font-size: 1.1rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.model-description {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  min-height: 2.7rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.model-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  color: #64748b;
}

.model-stats span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.model-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.category-tag.more {
  background: #e2e8f0;
  color: #64748b;
}

.model-actions {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  gap: 0.5rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.modal-body {
  padding: 1.5rem;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control.file-input {
  padding: 0.5rem;
}

.form-help {
  font-size: 0.85rem;
  color: #64748b;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.alert-error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.alert-success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-danger {
  background: #ef4444;
  color: white;
  width: 100%;
  justify-content: center;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .models-view {
    padding: 1rem;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
}
</style>
