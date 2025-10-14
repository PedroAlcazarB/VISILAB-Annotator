<template>
  <div class="categories-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>
            <i class="fas fa-tags"></i>
            Categorías
          </h1>
          <p class="subtitle">Gestiona las categorías de anotación para tus proyectos</p>
        </div>
        <div class="header-actions">
          <button @click="showCreateModal = true" class="btn btn-primary">
            <i class="fas fa-plus"></i>
            Crear Categoría
          </button>
          <button @click="refreshCategories" class="btn btn-secondary">
            <i class="fas fa-sync-alt"></i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Categories Grid -->
    <div class="categories-container">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Cargando categorías...</p>
      </div>

      <div v-else-if="categories.length === 0" class="empty-state">
        <i class="fas fa-tags"></i>
        <h3>No hay categorías</h3>
        <p>Crea tu primera categoría para comenzar a anotar</p>
        <button @click="showCreateModal = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Crear Primera Categoría
        </button>
      </div>

      <div v-else class="categories-grid">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-card"
          @click="selectCategory(category)"
        >
          <div class="card-header">
            <div class="category-title">
              <div 
                class="category-color" 
                :style="{ backgroundColor: category.color }"
              ></div>
              <h3>{{ category.name }}</h3>
            </div>
            <div class="card-actions">
              <button 
                @click.stop="editCategory(category)" 
                class="btn-icon btn-edit"
                title="Editar categoría"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                @click.stop="deleteCategory(category)" 
                class="btn-icon btn-delete"
                title="Eliminar categoría"
                :disabled="category.numberAnnotations > 0"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <div class="card-body">
            <div v-if="category.numberAnnotations > 0" class="annotation-count">
              <i class="fas fa-layer-group"></i>
              <span>{{ category.numberAnnotations }} anotaciones</span>
            </div>
            <div v-else class="annotation-count">
              <i class="fas fa-layer-group"></i>
              <span class="no-annotations">Sin anotaciones</span>
            </div>
          </div>

          <div class="card-footer">
            <span class="creator">
              <i class="fas fa-user"></i>
              Creado por {{ category.creator || 'Sistema' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para crear categoría -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="fas fa-plus"></i>
            Nueva Categoría
          </h2>
          <button @click="closeCreateModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="createCategory">
            <div class="form-group">
              <label for="categoryName">
                <i class="fas fa-tag"></i>
                Nombre de la categoría *
              </label>
              <input
                id="categoryName"
                v-model="newCategory.name"
                type="text"
                class="form-input"
                :class="{ 'error': errors.name }"
                placeholder="Ej: Persona, Vehículo, Animal..."
                required
              />
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="categoryColor">
                <i class="fas fa-palette"></i>
                Color
              </label>
              <div class="color-input-group">
                <input
                  id="categoryColor"
                  v-model="newCategory.color"
                  type="color"
                  class="form-color"
                />
                <input
                  v-model="newCategory.color"
                  type="text"
                  class="form-input color-text"
                  placeholder="#ff0000"
                />
              </div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button @click="createCategory" class="btn btn-primary" :disabled="creating">
            <i v-if="creating" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            {{ creating ? 'Creando...' : 'Crear Categoría' }}
          </button>
          <button @click="closeCreateModal" class="btn btn-secondary">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para editar categoría -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="fas fa-edit"></i>
            Editar Categoría: {{ editingCategory.name }}
          </h2>
          <button @click="closeEditModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="updateCategory">
            <div class="form-group">
              <label for="editCategoryName">
                <i class="fas fa-tag"></i>
                Nombre de la categoría *
              </label>
              <input
                id="editCategoryName"
                v-model="editingCategory.name"
                type="text"
                class="form-input"
                :class="{ 'error': errors.name }"
                required
              />
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="editCategoryColor">
                <i class="fas fa-palette"></i>
                Color
              </label>
              <div class="color-input-group">
                <input
                  id="editCategoryColor"
                  v-model="editingCategory.color"
                  type="color"
                  class="form-color"
                />
                <input
                  v-model="editingCategory.color"
                  type="text"
                  class="form-input color-text"
                  placeholder="#ff0000"
                />
              </div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button @click="updateCategory" class="btn btn-primary" :disabled="updating">
            <i v-if="updating" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            {{ updating ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
          <button @click="closeEditModal" class="btn btn-secondary">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Estado reactivo
const categories = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const creating = ref(false)
const updating = ref(false)
const errors = ref({})

const newCategory = ref({
  name: '',
  color: '#ff0000'
})

const editingCategory = ref({
  id: '',
  name: '',
  color: '#ff0000'
})

// Métodos
async function loadCategories() {
  loading.value = true
  try {
    const response = await fetch('/api/categories/data')
    const data = await response.json()
    
    if (response.ok) {
      categories.value = data.categories || []
    } else {
      console.error('Error al cargar categorías:', data.error)
      alert('Error al cargar categorías: ' + data.error)
    }
  } catch (error) {
    console.error('Error al cargar categorías:', error)
    alert('Error al cargar categorías')
  } finally {
    loading.value = false
  }
}

async function createCategory() {
  if (!validateForm(newCategory.value)) return
  
  creating.value = true
  errors.value = {}
  
  try {
    const response = await fetch('/api/categories', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newCategory.value)
    })
    
    const data = await response.json()
    
    if (response.ok) {
      alert('Categoría creada correctamente')
      closeCreateModal()
      await loadCategories()
    } else {
      alert('Error al crear categoría: ' + data.error)
    }
  } catch (error) {
    console.error('Error al crear categoría:', error)
    alert('Error al crear categoría')
  } finally {
    creating.value = false
  }
}

async function updateCategory() {
  if (!validateForm(editingCategory.value)) return
  
  updating.value = true
  errors.value = {}
  
  try {
    const response = await fetch(`/api/categories/${editingCategory.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: editingCategory.value.name,
        color: editingCategory.value.color
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      alert('Categoría actualizada correctamente')
      closeEditModal()
      await loadCategories()
    } else {
      alert('Error al actualizar categoría: ' + data.error)
    }
  } catch (error) {
    console.error('Error al actualizar categoría:', error)
    alert('Error al actualizar categoría')
  } finally {
    updating.value = false
  }
}

async function deleteCategory(category) {
  if (category.numberAnnotations > 0) {
    alert(`No se puede eliminar la categoría "${category.name}" porque tiene ${category.numberAnnotations} anotaciones asociadas.`)
    return
  }
  
  if (!confirm(`¿Estás seguro de que quieres eliminar la categoría "${category.name}"?`)) {
    return
  }
  
  try {
    const response = await fetch(`/api/categories/${category.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    
    if (response.ok) {
      alert('Categoría eliminada correctamente')
      await loadCategories()
    } else {
      alert('Error al eliminar categoría: ' + data.error)
    }
  } catch (error) {
    console.error('Error al eliminar categoría:', error)
    alert('Error al eliminar categoría')
  }
}

function validateForm(category) {
  errors.value = {}
  
  if (!category.name || category.name.trim() === '') {
    errors.value.name = 'El nombre es requerido'
    return false
  }
  
  if (category.name.length > 50) {
    errors.value.name = 'El nombre no puede exceder 50 caracteres'
    return false
  }
  
  return true
}

function editCategory(category) {
  editingCategory.value = {
    id: category.id,
    name: category.name,
    color: category.color
  }
  showEditModal.value = true
}

function selectCategory(category) {
  // Aquí puedes implementar la lógica para seleccionar una categoría
  console.log('Categoría seleccionada:', category)
}

function refreshCategories() {
  loadCategories()
}

function closeCreateModal() {
  showCreateModal.value = false
  newCategory.value = {
    name: '',
    color: '#ff0000'
  }
  errors.value = {}
}

function closeEditModal() {
  showEditModal.value = false
  editingCategory.value = {
    id: '',
    name: '',
    color: '#ff0000'
  }
  errors.value = {}
}

// Lifecycle
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories-view {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Header */
.page-header {
  background: white;
  border-bottom: 1px solid #e1e5e9;
  padding: 2rem 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-title h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
}

.header-title h1 i {
  margin-right: 0.5rem;
  color: #3498db;
}

.subtitle {
  margin: 0.5rem 0 0 0;
  color: #6c757d;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Categories Container */
.categories-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Loading & Empty States */
.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.loading-state i, .empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #3498db;
}

.empty-state h3 {
  margin: 1rem 0;
  color: #2c3e50;
}

/* Categories Grid */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  cursor: pointer;
  overflow: hidden;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f3f4;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.category-title h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
}

.category-color {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  flex-shrink: 0;
}

.card-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-icon {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
  color: #6c757d;
}

.btn-edit:hover {
  background: #fff3cd;
  color: #856404;
}

.btn-delete:hover:not(:disabled) {
  background: #f8d7da;
  color: #721c24;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-body {
  padding: 1rem 1.5rem;
  min-height: 80px;
}

.annotation-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.annotation-count i {
  color: #3498db;
}

.no-annotations {
  color: #6c757d;
  font-style: italic;
}

.card-footer {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #f1f3f4;
}

.creator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6c757d;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0.5rem;
  border-radius: 4px;
}

.btn-close:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e1e5e9;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* Forms */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-input.error {
  border-color: #e74c3c;
}

.color-input-group {
  display: flex;
  gap: 0.75rem;
}

.form-color {
  width: 60px;
  height: 45px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.color-text {
  flex: 1;
}

.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  display: block;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .categories-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .card-actions {
    align-self: flex-end;
  }
}
</style>