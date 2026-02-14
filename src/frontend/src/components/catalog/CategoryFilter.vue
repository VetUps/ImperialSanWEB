<template>
  <v-card>
    <v-card-title class="bg-primary text-white">
      <v-icon left>mdi-filter</v-icon>
      Категории
    </v-card-title>

    <v-card-text class="pa-0">
      <v-treeview
        :items="categoryTree"
        item-children="children"
        item-title="category_title"
        item-value="category_id"
        v-model:selected="selectedCategories"
        selectable
        return-object
        variant="plain"
        density="compact"
      >
        <template v-slot:prepend="{ item, open }">
          <v-icon size="small">
            {{ item.children 
              ? (open ? 'mdi-folder-open' : 'mdi-folder') 
              : 'mdi-package-variant' }}
          </v-icon>
        </template>
      </v-treeview>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions>
      <v-btn
        color="primary"
        variant="tonal"
        block
        @click="applyFilter"
        :disabled="!selectedCategory"
      >
        Применить фильтр
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, computed, watch, defineEmits, onMounted } from 'vue'
import { useCatalogStore } from '@/store/catalog'
import { storeToRefs } from 'pinia'

const catalogStore = useCatalogStore()
const { categoryTree } = storeToRefs(catalogStore)

const selectedCategories = ref([])
const emit = defineEmits(['filter'])

onMounted(() => {
  if (catalogStore.categories.length === 0) {
    catalogStore.fetchCategories()
  }
})

const selectedCategory = computed(() => {
  return selectedCategories.value.length > 0
    ? selectedCategories.value[0]
    : null
})

watch(selectedCategories, (newVal) => {
  if (newVal.length > 1) {
    selectedCategories.value = [newVal[newVal.length - 1]]
  }
})

const applyFilter = () => {
  if (selectedCategory.value) {
    emit('filter', selectedCategory.value.category_id)
  }
}
</script>