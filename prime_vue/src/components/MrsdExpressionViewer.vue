<template>
  <div class="mrsd-expression-viewer">
    <!-- Back button -->
    <div class="p-mb-3">
      <Button
        label="Back to Datasets"
        icon="pi pi-arrow-left"
        class="p-button-outlined"
        @click="$emit('back')"
      />
    </div>

    <!-- Dataset title -->
    <div class="dataset-header p-mb-4">
      <h2>MRSD-deep (expression)</h2>
      <div class="dataset-description">
        Calculate minimum required sequencing depth (MRSD) for your target genes
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="p-message p-message-error mb-3">
      <div class="p-message-wrapper">
        <span class="p-message-icon pi pi-times-circle"></span>
        <div class="p-message-text">{{ error }}</div>
      </div>
    </div>

    <div class="p-grid p-align-start mb-3">
      <!-- Gene Symbol -->
      <div class="p-col-12 p-md-4">
        <label for="geneSymbol" class="font-bold block mb-2">Gene Symbol(s):</label>
        <Textarea id="geneSymbol" v-model="searchGeneSymbols" rows="5" class="w-full" autoResize placeholder="Enter one gene symbol per line"/>
      </div>

      <!-- Target Count -->
      <div class="p-col-12 p-md-4">
        <label for="targetCount" class="font-bold block mb-2">Target Count:</label>
        <Dropdown id="targetCount" v-model="searchTargetCount" :options="[500, 1450, 2000]" placeholder="Select target count" class="w-full" />
      </div>

      <!-- Sample Type -->
      <div class="p-col-12 p-md-4">
        <label for="sampleType" class="font-bold block mb-2">Sample Type:</label>
        <Dropdown id="sampleType" v-model="searchSampleType" :options="['Blood', 'Fibroblast', 'IPSC', 'LCL']" placeholder="Select sample type" class="w-full" />
      </div>

      <!-- Search Button -->
      <div class="p-col-12 mt-3">
        <Button label="Search" icon="pi pi-search" class="w-full" @click="onSearch" />
      </div>
    </div>

    <!-- Export Button -->
    <div class="p-mb-3 text-right">
      <Button
        label="Export CSV"
        icon="pi pi-download"
        class="p-button-success"
        :disabled="loading"
        @click="exportCSV"
      />
    </div>

    <!-- Data Table with expression-specific styling -->
    <div class="card">
      <DataTable
        :value="tableData"
        :paginator="true"
        :rows="rowsPerPage"
        :totalRecords="totalRecords"
        :loading="loading"
        :lazy="true"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 20, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
        responsiveLayout="scroll"
        @page="onPageChange($event)"
        :first="(currentPage - 1) * rowsPerPage"
        stripedRows
        class="p-datatable-sm"
      >
        <template #empty>
          <div class="p-d-flex p-flex-column p-ai-center empty-message">
            <i class="pi pi-exclamation-circle" style="font-size: 2rem; margin-bottom: 0.5rem; color: #e24c4c;"></i>
            <p v-if="error">{{ error }}</p>
            <p v-else-if="!loading">No data found. Try removing any search filters.</p>
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
            <span v-if="data[field] === 'Infinity' || data[field] === '-Infinity' || data[field] === 'NaN'" class="special-value">
              {{ data[field] }}
            </span>
            <span v-else-if="field === 'hgnc_symbol'" class="gene-symbol">
              {{ data[field] }}
            </span>
            <span v-else>
              {{ data[field] }}
            </span>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import qs from 'qs'
import Textarea from 'primevue/textarea';

export default {
  name: 'MrsdExpressionViewer',
  components: {
    Textarea
  },
  data() {
    return {
      columns: [],
      selectedColumn: null,
      searchQuery: '',
      searchGeneSymbols: '',
      searchTargetCount: null,
      searchSampleType: null,
      tableData: [],
      loading: false,
      totalRecords: 0,
      currentPage: 1,
      rowsPerPage: 10,
      error: null,
      dataset: 'mrsd_expression'
    }
  },
  created() {
    this.fetchColumns();
    this.fetchData(1);
  },
  methods: {
    formatDatasetName(name) {
      // Convert snake_case to Title Case with spaces
      return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    },

    async fetchColumns() {
      const baseUrl =
        process.env.NODE_ENV === 'development'
          ? 'http://localhost:8000'
          : '';
      this.loading = true
      try {
        const response = await axios.get(`${baseUrl}/api/columns/${this.dataset}`)
        this.columns = response.data
        this.selectedColumn = null
      } catch (error) {
        console.error('Error fetching columns:', error)
        this.error = `Failed to fetch columns for dataset ${this.dataset}. Please ensure the backend server is running.`;
      } finally {
        this.loading = false
      }
    },

    async fetchData(page = 1) {
      const baseUrl =
        process.env.NODE_ENV === 'development'
          ? 'http://localhost:8000'
          : '';
      this.loading = true
      this.error = null
      try {
        // Update current page
        this.currentPage = page;

        const params = {
          page: page,
          per_page: this.rowsPerPage
        }

        // Standard timeout for normal-sized datasets
        const timeoutMs = 10000; // 10 seconds

        console.log('searchGeneSymbols:', this.searchGeneSymbols);

        if (this.searchGeneSymbols) {
          // Support both repeated param (?gene_symbols=A&gene_symbols=B) and comma-separated (?gene_symbols=A,B)
          // Here we always send as repeated params (array), splitting on lines
          params.gene_symbols = this.searchGeneSymbols.split('\n').map(s => s.trim()).filter(s => s);
        }
        if (this.searchTargetCount !== null) {
          params.target_count = this.searchTargetCount;
        }
        if (this.searchSampleType) {
          params.sample_type = this.searchSampleType;
        }

        console.log(`Fetching data for ${this.dataset} with params:`, params);

        // Start a timer to measure the request duration
        const requestStartTime = new Date().getTime();

        // Add timeout and validation options
        const response = await axios.get(`${baseUrl}/api/data/${this.dataset}`, {
          params,
          timeout: timeoutMs,
          validateStatus: function (status) {
            return status < 500; // Only reject if server error
          },
          paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
        });

        // Calculate how long the request took
        const requestDuration = new Date().getTime() - requestStartTime;
        console.log(`Request completed in ${requestDuration/1000} seconds`);

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

            // Make sure we get the correct per_page value from the response
            if (responseData.per_page) {
              this.rowsPerPage = responseData.per_page;
            }

            console.log(`Updated pagination state: page ${this.currentPage}, ${this.rowsPerPage} rows per page, total ${this.totalRecords} records`);

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
      this.currentPage = 1;
      this.fetchData(1);
    },

    onPageChange(event) {
      console.log('Page change event:', event);
      const newPage = Math.floor(event.first / event.rows) + 1;
      this.rowsPerPage = event.rows;
      console.log(`Changing page to ${newPage} with ${this.rowsPerPage} rows per page`);
      this.fetchData(newPage);
    },

    exportCSV() {
      const baseUrl =
        process.env.NODE_ENV === 'development'
          ? 'http://localhost:8000'
          : '';
      const params = new URLSearchParams();
      params.append('per_page', this.rowsPerPage);
      if (this.searchGeneSymbols) {
        const genes = this.searchGeneSymbols.split('\n').map(s => s.trim()).filter(s => s);
        for (const gene of genes) {
          params.append('gene_symbols', gene);
        }
      }
      if (this.searchTargetCount !== null) {
        params.append('target_count', this.searchTargetCount);
      }
      if (this.searchSampleType) {
        params.append('sample_type', this.searchSampleType);
      }
      const url = `${baseUrl}/api/export/${this.dataset}?${params.toString()}`;
      window.open(url, '_blank');
    },
  }
}
</script>

<style scoped>
.mrsd-expression-viewer {
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

.dataset-description {
  color: #666;
  margin-top: 0.5rem;
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

.gene-symbol {
  font-weight: bold;
  color: #3498db;
}

.text-right {
  text-align: right;
}
</style>
