<template>
  <div class="dataset-cards">
    <h2 class="section-title">Available Resources</h2>

    <!-- Loading indicator -->
    <div v-if="loading" class="p-d-flex p-flex-column p-ai-center">
      <ProgressSpinner />
      <p>Loading datasets...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="error" class="p-message p-message-error mb-3">
      <div class="p-message-wrapper">
        <span class="p-message-icon pi pi-times-circle"></span>
        <div class="p-message-text">{{ error }}</div>
      </div>
    </div>

    <!-- Sample Data Warning -->
    <div v-if="usingSampleData" class="p-message p-message-warning mb-3">
      <div class="p-message-wrapper">
        <span class="p-message-icon pi pi-exclamation-triangle"></span>
        <div class="p-message-text">
          <strong>Using sample data:</strong> The application is currently using sample data because the actual TSV files couldn't be loaded.
          Please check that the data files exist in the 'data' folder and are in the correct format.
        </div>
      </div>
    </div>

    <!-- Dataset cards -->
    <div v-else class="p-grid">
      <div v-for="(dataset, index) in datasets" :key="dataset" class="p-col-12 p-md-4 p-mb-3">
        <div class="card dataset-card" @click="selectDataset(dataset)">
          <div class="card-header" :class="'dataset-' + (index % 3 + 1)">
            <i class="pi pi-database"></i>
          </div>
          <div class="card-body">
            <h3>{{ formatDatasetName(dataset) }}</h3>
            <p>{{ getDatasetDescription(dataset) }}</p>
            <div class="dataset-meta">
              <span><i class="pi pi-table"></i> {{ datasetStats[dataset]?.columns || '?' }} columns</span>
              <span><i class="pi pi-list"></i> {{ datasetStats[dataset]?.rows || '?' }} rows</span>
            </div>
            <Button
              label="View Dataset"
              icon="pi pi-eye"
              class="p-button-outlined p-mt-3"
              @click.stop="selectDataset(dataset)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DatasetCards',
  data() {
    return {
      datasets: [],
      loading: false,
      error: null,
      usingSampleData: false,
      datasetStats: {}
    }
  },
  created() {
    this.fetchDatasets();
  },
  methods: {
    async fetchDatasets() {
      this.loading = true;
      this.error = null;

      const baseUrl = `http://${window.location.hostname}:8000`;
      console.log(`Connecting to backend at: ${baseUrl}`);

      try {
        const response = await axios.get(`${baseUrl}/api/datasets`, { timeout: 5000 })
        let datasets = response.data

        // Sort datasets in desired order: mrsd_splice, mrsd_expression, splice_vault
        const desiredOrder = ['mrsd_splice', 'mrsd_expression', 'splice_vault'];

        // Sort datasets according to the desired order
        datasets.sort((a, b) => {
          const indexA = desiredOrder.indexOf(a);
          const indexB = desiredOrder.indexOf(b);

          // If both items are in our desired order array, sort by that order
          if (indexA !== -1 && indexB !== -1) {
            return indexA - indexB;
          }
          // If only a is in the desired order array, it comes first
          if (indexA !== -1) {
            return -1;
          }
          // If only b is in the desired order array, it comes first
          if (indexB !== -1) {
            return 1;
          }
          // If neither is in the desired order array, maintain original order
          return 0;
        });

        this.datasets = datasets;

        if (this.datasets.length === 0) {
          this.error = 'No datasets available. Please check that the data files exist and are in the correct format.';
        } else {
          // Check if we're using sample data and get dataset stats
          await this.fetchDatasetStats(baseUrl);
        }
      } catch (error) {
        console.error('Error fetching datasets:', error)
        this.error = `Failed to connect to the server at ${baseUrl}. Please make sure the backend is running and accessible.`;
      } finally {
        this.loading = false;
      }
    },

    async fetchDatasetStats(baseUrl) {
      try {
        // Get stats for each dataset
        for (const dataset of this.datasets) {
          const columnsResponse = await axios.get(`${baseUrl}/api/columns/${dataset}`);
          const columns = columnsResponse.data.length;

          const dataResponse = await axios.get(`${baseUrl}/api/data/${dataset}`, {
            params: { page: 1, per_page: 1 }
          });
          const rows = dataResponse.data.total;

          this.datasetStats[dataset] = { columns, rows };

          // If each dataset has exactly 3 or 5 rows, it's likely our sample data
          if (rows <= 5) {
            this.usingSampleData = true;
          }
        }
      } catch (error) {
        console.error('Error fetching dataset stats:', error);
      }
    },

    formatDatasetName(dataset) {
      // Convert snake_case to Title Case with spaces
      const name = {
        'mrsd_splice': 'MRSD-deep (splice)',
        'splice_vault': 'SpliceVault-deep (deep RNAseq)',
        'mrsd_expression': 'MRSD-deep (expression)'
      };

      return name[dataset];
    },

    getDatasetDescription(dataset) {
      const descriptions = {
        'mrsd_splice': 'Calculate minimum required sequencing depth (MRSD) for your target splice junctions.',
        'splice_vault': 'Find naturally occurring alternative splicing identified by deep RNA-seq.',
        'mrsd_expression': 'Calculate minimum required sequencing depth (MRSD) for your target genes.'
      };

      return descriptions[dataset] || 'Dataset containing TSV data.';
    },

    selectDataset(dataset) {
      this.$emit('dataset-selected', dataset);
    }
  }
}
</script>

<style scoped>
.dataset-cards {
  margin-bottom: 2rem;
}

.section-title {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-weight: 600;
  text-align: center;
}

.dataset-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
}

.dataset-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.card-header {
  padding: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
}

.card-header i {
  font-size: 2.5rem;
}

.dataset-1 {
  background: linear-gradient(135deg, #42b883 0%, #2f9c6a 100%);
}

.dataset-2 {
  background: linear-gradient(135deg, #4a7feb 0%, #2f58c6 100%);
}

.dataset-3 {
  background: linear-gradient(135deg, #f06292 0%, #d81b60 100%);
}

.card-body {
  padding: 1.5rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}

.card-body h3 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  color: #2c3e50;
  font-weight: 600;
}

.card-body p {
  margin-bottom: 1rem;
  color: #5c6370;
  flex-grow: 1;
}

.dataset-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.dataset-meta span {
  display: flex;
  align-items: center;
}

.dataset-meta i {
  margin-right: 0.5rem;
}

.mb-3 {
  margin-bottom: 1rem;
}
</style>
