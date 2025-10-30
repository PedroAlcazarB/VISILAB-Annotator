<template>
  <div class="categories-manager">
    <!-- Header -->
    <div class="categories-header">
      <h3>Gestión de Categorías</h3>
      <button @click="showAddForm = true" class="btn-primary">
        + Nueva Categoría
      </button>
    </div>

    <!-- Formulario para nueva categoría -->
    <div v-if="showAddForm" class="add-form">
      <h4>Nueva Categoría</h4>
      <div class="form-group">
        <label>Nombre:</label>
        <input 
          v-model="newCategory.name" 
          type="text" 
          class="form-input"
          placeholder="Nombre de la categoría"
        >
      </div>
      <div class="form-group">
        <label>Color:</label>
        <input 
          v-model="newCategory.color" 
          type="color" 
          class="form-color"
        >
      </div>
      <div class="form-actions">
        <button @click="addCategory" class="btn-success" :disabled="adding">
          {{ adding ? 'Añadiendo...' : 'Añadir' }}
        </button>
        <button @click="cancelAdd" class="btn-secondary">Cancelar</button>
      </div>
    </div>

    <!-- Lista de categorías -->
    <div class="categories-list">
      <div v-if="loading" class="loading-state">
        <p>Cargando categorías...</p>
      </div>
      
      <div v-else-if="categories.length === 0" class="empty-state">
        <p>No hay categorías disponibles</p>
        <button @click="showAddForm = true" class="btn-primary">
          Crear primera categoría
        </button>
      </div>
      
      <div 
        v-else
        v-for="category in categories" 
        :key="category.id" 
        class="category-section"
      >
        <!-- Header de la categoría -->
        <div 
          class="category-header"
          :class="{ 
            'active': selectedCategory === category.id,
            'hidden-category': isHidden(category.id)
          }"
          @click="selectCategory(category.id)"
        >
          <div class="category-info">
            <div 
              class="category-color" 
              :style="{ backgroundColor: category.color }"
            ></div>
            <div class="category-details">
              <span class="category-name">{{ category.name }}</span>
            </div>
            <span class="category-count">({{ getCategoryAnnotationCount(category.id) }})</span>
          </div>
          <div class="category-actions">
            <button 
              @click.stop="editCategory(category)" 
              class="btn-edit"
              title="Editar categoría"
            >
              ✏️
            </button>
            <button 
              @click.stop="toggleVisibility(category.id)" 
              class="btn-visibility"
              :title="isHidden(category.id) ? 'Mostrar categoría' : 'Ocultar categoría'"
            >
              👁️
            </button>
          </div>
        </div>

        <!-- Lista de anotaciones de esta categoría -->
        <div 
          v-if="getCategoryAnnotations(category.id).length > 0" 
          class="annotations-list"
        >
          <div 
            v-for="(annotation, index) in getCategoryAnnotations(category.id)" 
            :key="annotation._id"
            class="annotation-item"
            :class="{ 'hidden-annotation': isAnnotationHidden(annotation._id) }"
            @click="selectAnnotation(annotation)"
          >
            <span class="annotation-number">{{ index + 1 }}</span>
            <span class="annotation-id">(id: {{ annotation._id.slice(-2) }})</span>
            <div class="annotation-actions">
              <button 
                @click.stop="toggleAnnotationVisibility(annotation._id)" 
                class="btn-visibility-small"
                :title="isAnnotationHidden(annotation._id) ? 'Mostrar anotación' : 'Ocultar anotación'"
              >
                👁️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de edición -->
    <div v-if="editingCategory" class="modal-overlay" @click="cancelEdit">
      <div class="modal-content" @click.stop>
        <h4>Editar Categoría</h4>
        <div class="form-group">
          <label>Nombre:</label>
          <input 
            v-model="editingCategory.name" 
            type="text" 
            class="form-input"
          >
        </div>
        <div class="form-group">
          <label>Color:</label>
          <input 
            v-model="editingCategory.color" 
            type="color" 
            class="form-color"
          >
        </div>
        <div class="form-actions">
          <button @click="saveEdit" class="btn-success">Guardar</button>
          <button @click="cancelEdit" class="btn-secondary">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Categoría seleccionada actual -->
    <div v-if="selectedCategory" class="current-selection">
      <div class="selected-category">
        <div 
          class="category-color small" 
          :style="{ backgroundColor: selectedCategoryData?.color }"
        ></div>
        <span>Categoría: {{ selectedCategoryData?.name }}</span>
      </div>
      <p class="help-text">Las nuevas anotaciones se asignarán a esta categoría</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAnnotationStore } from '../stores/annotationStore'

// Store
const store = useAnnotationStore()

// Estado reactivo
const categories = computed(() => store.categories)
const annotations = computed(() => store.annotations)
const loading = computed(() => store.loading)
const selectedCategory = computed(() => store.selectedCategory)

const selectedCategoryData = computed(() => {
  return categories.value.find(cat => cat.id === selectedCategory.value)
})

const showAddForm = ref(false)
const adding = ref(false)
const editingCategory = ref(null)

const newCategory = ref({
  name: '',
  color: '#ff0000'
})

// Métodos
function selectCategory(categoryId) {
  store.setSelectedCategory(categoryId)
}

async function addCategory() {
  if (!newCategory.value.name.trim()) return
  
  adding.value = true
  try {
    await store.addCategory(newCategory.value)
    newCategory.value = { name: '', color: '#ff0000' }
    showAddForm.value = false
  } catch (error) {
    // El error ya se maneja en el store
  } finally {
    adding.value = false
  }
}

function cancelAdd() {
  showAddForm.value = false
  newCategory.value = { name: '', color: '#ff0000' }
}

function editCategory(category) {
  editingCategory.value = { ...category }
}

async function saveEdit() {
  try {
    await store.updateCategory(editingCategory.value)
    editingCategory.value = null
  } catch (error) {
    // El error ya se maneja en el store
  }
}

function cancelEdit() {
  editingCategory.value = null
}

function getCategoryAnnotationCount(categoryId) {
  return store.getCategoryAnnotationCount(categoryId)
}

// Función para verificar si una categoría está oculta
function isHidden(categoryId) {
  return store.isCategoryHidden(categoryId)
}

// Función para toggle visibilidad
async function toggleVisibility(categoryId) {
  try {
    await store.toggleCategoryVisibility(categoryId)
  } catch (error) {
    console.error('Error al cambiar visibilidad:', error)
  }
}

// Nuevas funciones para manejar anotaciones individuales
function getCategoryAnnotations(categoryId) {
  // Usar el nuevo getter que filtra por imagen actual
  const annotationsByCategory = store.getCurrentImageAnnotationsByCategory
  return annotationsByCategory[categoryId] || []
}

function isAnnotationHidden(annotationId) {
  return store.isAnnotationHidden(annotationId)
}

function toggleAnnotationVisibility(annotationId) {
  store.toggleAnnotationVisibility(annotationId)
}

function selectAnnotation(annotation) {
  store.selectAnnotation(annotation)
}

// Cargar categorías al montar el componente
onMounted(() => {
  if (categories.value.length === 0) {
    store.loadCategories()
  }
  // Cargar anotaciones del dataset actual (si hay uno) o todas si no hay dataset
  if (annotations.value.length === 0) {
    if (store.currentDataset) {
      store.loadAnnotationsByDataset()
      store.loadCategoryVisibility()
    } else {
      store.loadAllAnnotations()
    }
  }
})
</script>

<style scoped>
.categories-manager {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.categories-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.categories-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
}

.btn-primary {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
}

.btn-primary:hover {
  background: #2980b9;
}

.add-form {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
}

.add-form h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-color {
  width: 50px;
  height: 35px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-success {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-success:hover {
  background: #229954;
}

.btn-success:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.category-section {
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-bottom: 1px solid #e1e5e9;
  cursor: pointer;
  transition: background-color 0.2s;
}

.category-header:hover {
  background: #f8f9fa;
}

.category-header.active {
  border-color: #27ae60;
  background: #f8fff9;
}

.category-header.hidden-category {
  opacity: 0.5;
  background: #f5f5f5;
}

.category-header.hidden-category .category-color {
  opacity: 0.6;
}

.category-header.hidden-category .category-name {
  color: #999;
  text-decoration: line-through;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.category-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.1);
}

.category-color.small {
  width: 12px;
  height: 12px;
}

.category-details {
  flex: 1;
}

.category-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.category-count {
  color: #666;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}

.category-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-edit, .btn-delete, .btn-visibility {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 3px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-edit:hover, .btn-delete:hover, .btn-visibility:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

.annotations-list {
  background: #f8f9fa;
  border-top: 1px solid #e1e5e9;
}

.annotation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e1e5e9;
  cursor: pointer;
  transition: background-color 0.2s;
}

.annotation-item:last-child {
  border-bottom: none;
}

.annotation-item:hover {
  background: #e9ecef;
}

.annotation-item.hidden-annotation {
  opacity: 0.5;
  background: #f5f5f5;
  text-decoration: line-through;
}

.annotation-number {
  font-weight: 600;
  color: #3498db;
  font-size: 0.9rem;
}

.annotation-id {
  color: #666;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

.annotation-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-visibility-small {
  background: none;
  border: none;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.1rem;
  border-radius: 3px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-visibility-small:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

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
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  min-width: 300px;
  max-width: 500px;
}

.modal-content h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.current-selection {
  background: #e8f5e8;
  border: 1px solid #27ae60;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.selected-category {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #27ae60;
}

.help-text {
  margin: 0.5rem 0 0 0;
  font-size: 0.9rem;
  color: #666;
}
</style>