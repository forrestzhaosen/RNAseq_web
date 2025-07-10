<template>
  <div class="data-viewer">
    <!-- Dataset Cards View (when no dataset is selected) -->
    <div v-if="!selectedDataset">
      <DatasetCards @dataset-selected="selectDataset" />
    </div>

    <!-- Dataset Detail View (when a dataset is selected) -->
    <div v-else>
      <!-- Back button -->
      <div class="p-mb-3">
        <Button
          label="Back to Datasets"
          icon="pi pi-arrow-left"
          class="p-button-outlined"
          @click="backToDatasets"
        />
      </div>

      <!-- Dataset title -->
      <div class="dataset-header p-mb-4">
        <h2>{{ formatDatasetName(selectedDataset) }}</h2>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="p-message p-message-error mb-3">
        <div class="p-message-wrapper">
          <span class="p-message-icon pi pi-times-circle"></span>
          <div class="p-message-text">{{ error }}</div>
        </div>
      </div>

    <!-- Search and Filter -->
    <div class="p-grid p-align-center mb-3">
      <div class="p-col-12 p-md-4">
        <label for="column" class="font-bold block mb-2">Search Column:</label>
        <Dropdown id="column" v-model="selectedColumn" :options="columns"
                 placeholder="Select column" class="w-full" />
      </div>
      <div class="p-col-12 p-md-6">
        <label for="search" class="font-bold block mb-2">Search Term:</label>
        <span class="p-input-icon-right w-full">
          <i class="pi pi-search" />
          <InputText id="search" v-model="searchQuery" placeholder="Enter search term"
                    class="w-full" />
        </span>
      </div>
      <div class="p-col-12 p-md-2 flex align-items-end">
        <Button label="Search" icon="pi pi-search" class="w-full" @click="onSearch" />
      </div>
    </div>

    <!-- Data Table -->
    <div class="card">
      <DataTable
        :value="tableData"
        :paginator="true"
        :rows="10"
        :totalRecords="totalRecords"
        :loading="loading"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 20, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
        responsiveLayout="scroll"
        @page="onPageChange($event)"
        stripedRows
        class="p-datatable-sm"
      >
        <template #empty>
          <div class="p-d-flex p-flex-column p-ai-center empty-message">
            <i class="pi pi-exclamation-circle" style="font-size: 2rem; margin-bottom: 0.5rem; color: #e24c4c;"></i>
            <p v-if="error">{{ error }}</p>
            <p v-else-if="!loading">No data found for the selected dataset. Try removing any search filters.</p>
          </div>
        </template>
        <template #loading>
          <div class="p-d-flex p-flex-column p-ai-center">
            <ProgressSpinner style="width: 50px; height: 50px;" />
            <p>Loading data...</p>
          </div>
        </template>
        <Column v-for="col in columns" :key="col" :field="col" :header="col" sortable>
          <template #body="{ data, field }">
            {{ data[field] }}
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
  </div>
</template>

<script>
import axios from 'axios'
import DatasetCards from './DatasetCards.vue'

export default {
  name: 'DataViewer',
  components: {
    DatasetCards
  },
  data() {
    return {
      datasets: [],
      selectedDataset: null,
      columns: [],
      selectedColumn: null,
      searchQuery: '',
      tableData: [],
      loading: false,
      totalRecords: 0,
      currentPage: 1,
      error: null,
      usingSampleData: false
    }
  },
  created() {
    this.fetchDatasets()
  },
  methods: {
    selectDataset(dataset) {
      this.selectedDataset = dataset;
      this.fetchColumns();
      this.fetchData(1);
    },

    backToDatasets() {
      this.selectedDataset = null;
      this.tableData = [];
      this.error = null;
    },

    formatDatasetName(name) {
      // Convert snake_case to Title Case with spaces
      return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    },

    async fetchDatasets() {
      this.loading = true;
      this.error = null;

      // Base URL for API requests - using window.location.hostname to make it work in any environment
      // Using port 8000 instead of 5000 to avoid conflicts with AirPlay on macOS
      const baseUrl = `http://${window.location.hostname}:8000`;
      console.log(`Connecting to backend at: ${baseUrl}`);

      try {
        const response = await axios.get(`${baseUrl}/api/datasets`, { timeout: 5000 })
        this.datasets = response.data

        if (this.datasets.length === 0) {
          this.error = 'No datasets available. Please check that the data files exist and are in the correct format.';
        } else {
          // Check if we're using sample data by examining the size of the first dataset
          this.checkForSampleData(baseUrl);
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

    async checkForSampleData(baseUrl) {
      try {
        if (this.datasets.length > 0) {
          const dataset = this.datasets[0];
          const response = await axios.get(`${baseUrl}/api/data/${dataset}`, {
            params: { page: 1, per_page: 10 }
          });

          // If each dataset has exactly 3 or 5 rows, it's likely our sample data
          if (response.data.total <= 5) {
            this.usingSampleData = true;
          } else {
            this.usingSampleData = false;
          }
        }
      } catch (error) {
        console.error('Error checking for sample data:', error);
      }
    },
    async fetchColumns() {
      if (!this.selectedDataset) return

      const baseUrl = `http://${window.location.hostname}:8000`;
      this.loading = true
      try {
        const response = await axios.get(`${baseUrl}/api/columns/${this.selectedDataset}`)
        this.columns = response.data
        this.selectedColumn = null
      } catch (error) {
        console.error('Error fetching columns:', error)
        this.error = `Failed to fetch columns for dataset ${this.selectedDataset}. Please ensure the backend server is running.`;
      } finally {
        this.loading = false
      }
    },
    async fetchData(page = 1) {
      if (!this.selectedDataset) return

      const baseUrl = `http://${window.location.hostname}:8000`;
      this.loading = true
      this.error = null
      try {
        // Use smaller page size for large datasets
        const params = {
          page: page,
          per_page: 5 // Reduced from 10 to ensure smaller payload
        }

        if (this.searchQuery && this.selectedColumn) {
          params.search = this.searchQuery
          params.column = this.selectedColumn
        }

        console.log(`Fetching data for ${this.selectedDataset} with params:`, params);
        // Add timeout and validation options
        const response = await axios.get(`${baseUrl}/api/data/${this.selectedDataset}`, {
          params,
          timeout: 10000, // 10 second timeout
          validateStatus: function (status) {
            return status < 500; // Only reject if server error
          }
        })
        console.log('Response data:', response.data);

        // Check for HTTP errors first
        if (response.status !== 200) {
          console.error(`Server returned status code ${response.status}`);
          this.error = `Server error (${response.status}): ${response.statusText}`;
          this.tableData = [];
          this.totalRecords = 0;
          return;
        }

        // Handle server-side error messages
        if (response.data && response.data.error) {
          console.error('Server returned error:', response.data.error);
          this.error = response.data.error;
          this.tableData = [];
          this.totalRecords = 0;
          return;
        }

        // Safe access to data array
        const responseData = response.data;
        const dataArray = responseData && responseData.data;

        if (dataArray && Array.isArray(dataArray)) {
          try {
            // Sanitize the data to handle any potential issues
            const sanitizedData = [];

            for (const item of dataArray) {
              // Skip null or undefined items
              if (!item) continue;

              const cleanItem = {};

              // Process each column safely
              this.columns.forEach(col => {
                try {
                  // Handle various data types appropriately
                  if (item[col] === null || item[col] === undefined) {
                    cleanItem[col] = '';
                  } else if (typeof item[col] === 'object') {
                    // Convert objects to strings to avoid rendering issues
                    cleanItem[col] = JSON.stringify(item[col]);
                  } else {
                    cleanItem[col] = item[col];
                  }
                } catch (e) {
                  console.warn(`Error processing column ${col}:`, e);
                  cleanItem[col] = '';
                }
              });

              sanitizedData.push(cleanItem);
            }

            this.tableData = sanitizedData;
            this.totalRecords = responseData.total || 0;
            this.currentPage = page;

            if (this.tableData.length === 0) {
              console.warn('Received empty data array from server');
            }
          } catch (e) {
            console.error('Error processing response data:', e);
            this.error = `Error processing data: ${e.message}`;
            this.tableData = [];
            this.totalRecords = 0;
          }
        } else {
          console.error('Invalid response format:', responseData);
          this.error = 'Received invalid data format from the server';
          this.tableData = [];
          this.totalRecords = 0;
        }
      } catch (error) {
        console.error('Error fetching data:', error);

        // Try to provide a more specific error message
        if (error.response) {
          // The request was made and the server responded with a status code
          console.error('Server response:', error.response.status, error.response.data);
          if (error.response.data && error.response.data.error) {
            this.error = `Server error: ${error.response.data.error}`;
          } else {
            this.error = `Server error (${error.response.status}): ${error.response.statusText}`;
          }
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received');
          this.error = 'No response received from server. Please check your network connection.';
        } else if (error.message && error.message.includes('timeout')) {
          // Request timed out
          this.error = 'Request timed out. The dataset may be too large to process.';
        } else {
          // Something else happened
          this.error = `Error: ${error.message || 'Unknown error'}`;
        }

        this.tableData = [];
        this.totalRecords = 0;
      } finally {
        this.loading = false;
      }
    },
    onSearch() {
      this.fetchData(1)
    },
    onPageChange(event) {
      this.fetchData(event.page + 1)
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
</style>
