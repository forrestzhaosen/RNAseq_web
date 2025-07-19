<template>
  <div class="data-viewer">
    <!-- Dataset Cards View (when no dataset is selected) -->
    <div v-if="!selectedDataset">
      <DatasetCards @dataset-selected="selectDataset" />
    </div>

    <!-- Specialized Dataset Viewers -->
    <MrsdSpliceViewer v-else-if="selectedDataset === 'mrsd_splice'" @back="backToDatasets" />
    <SpliceVaultViewer v-else-if="selectedDataset === 'splice_vault'" @back="backToDatasets" />
    <MrsdExpressionViewer v-else-if="selectedDataset === 'mrsd_expression'" @back="backToDatasets" />
  </div>
</template>

<script>
import axios from 'axios'
import DatasetCards from './DatasetCards.vue'
import MrsdSpliceViewer from './MrsdSpliceViewer.vue'
import SpliceVaultViewer from './SpliceVaultViewer.vue'
import MrsdExpressionViewer from './MrsdExpressionViewer.vue'

export default {
  name: 'DataViewer',
  components: {
    DatasetCards,
    MrsdSpliceViewer,
    SpliceVaultViewer,
    MrsdExpressionViewer
  },
  data() {
    return {
      datasets: [],
      selectedDataset: null,
      loading: false,
      error: null,
      columns: [], // Keep these for backward compatibility
      tableData: [],
      rowsPerPage: 10,
      currentPage: 1,
      totalRecords: 0,
      searchQuery: '',
      selectedColumn: null
    }
  },
  created() {
    this.fetchDatasets()
  },
  methods: {
    selectDataset(dataset) {
      this.selectedDataset = dataset;
    },

    backToDatasets() {
      this.selectedDataset = null;
    },

    async fetchDatasets() {
      this.loading = true;
      this.error = null;

      // Base URL for API requests - using relative URL to work with nginx proxy
      const baseUrl =
        process.env.NODE_ENV === 'development'
          ? 'http://localhost:8000'
          : '';
      console.log(`Connecting to backend with base URL: ${baseUrl}`);

      try {
        const response = await axios.get(`${baseUrl}/api/datasets`, { timeout: 5000 })
        this.datasets = response.data

        if (this.datasets.length === 0) {
          this.error = 'No datasets available. Please check that the data files exist and are in the correct format.';
        }
      } catch (error) {
        console.error('Error fetching datasets:', error)
        this.error = `Failed to connect to the server at ${baseUrl}. Please make sure the backend is running and accessible.`;
        // Show more detailed error information in the console
        if (error.response) {
          // The request was made and the server responded with a status code
          console.error('Server responded with error:', error.response.status, error.response.data);
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received from server');
        } else {
          // Something happened in setting up the request
          console.error('Request setup error:', error.message);
        }
      } finally {
        this.loading = false;
      }
    },

    // Empty placeholder methods to prevent errors
    onSearch() {
      console.log('Search functionality moved to child components');
    },

    onPageChange() {
      console.log('Pagination functionality moved to child components');
    }
  }
}
</script>

<style scoped>
.data-viewer {
  padding: 1rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.p-mb-3 {
  margin-bottom: 1rem;
}

.p-mb-4 {
  margin-bottom: 1.5rem;
}

.w-full {
  width: 100%;
}

.font-bold {
  font-weight: bold;
}

.block {
  display: block;
}

.card {
  background: #ffffff;
  border-radius: 4px;
  padding: 1rem;
  box-shadow: 0 2px 1px -1px rgba(0,0,0,0.2), 0 1px 1px 0 rgba(0,0,0,0.14), 0 1px 3px 0 rgba(0,0,0,0.12);
}

.flex {
  display: flex;
}

.align-items-end {
  align-items: flex-end;
}

.dataset-header {
  text-align: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.dataset-header h2 {
  color: #2c3e50;
  font-weight: 600;
  margin: 0;
}

.empty-message {
  padding: 2rem;
  text-align: center;
  color: #6c757d;
}

.p-d-flex {
  display: flex;
}

.p-flex-column {
  flex-direction: column;
}

.p-ai-center {
  align-items: center;
}

.special-value {
  color: #e74c3c;
  font-style: italic;
  font-weight: bold;
}
</style>
