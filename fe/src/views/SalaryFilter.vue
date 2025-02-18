<template>
  <v-container>
    <!-- Filtre Kartı -->
    <v-card class="pa-4 mb-4">
      <v-card-title>Salary Survey Filtre</v-card-title>
      <v-card-text>
        <v-row>
          <!-- Title için select -->
          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="filters.title"
              :items="titleOptions"
              label="Pozisyon veya Seviye"
              outlined
              clearable
            />
          </v-col>

          <!-- Currency için select -->
          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="filters.currency"
              :items="currencyOptions"
              label="Para Birimi"
              outlined
              clearable
            />
          </v-col>

          <!-- Work Area için select -->
          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="filters.work_area"
              :items="workAreaOptions"
              label="Görev"
              outlined
              clearable
            />
          </v-col>

          <!-- Şirket Büyüklüğü Range Slider -->
          <v-col cols="12" sm="6" md="6">
            <v-range-slider
              v-model="filters.companySizeRange"
              :min="0"
              :max="500"
              step="10"
              label="Şirket Büyüklüğü Aralığı"
              thumb-label="always"
              ticks
            />
          </v-col>

          <!-- Tecrübe Range Slider -->
          <v-col cols="12" sm="6" md="6">
            <v-range-slider
              v-model="filters.experienceRange"
              :min="0"
              :max="30"
              step="2"
              label="Tecrübe Aralığı (yıl)"
              thumb-label="always"
              ticks
            />
          </v-col>
        </v-row>
        <v-row class="mt-2" justify="end">
          <v-col cols="auto">
            <v-btn color="secondary" @click="clearFilters"
              >Filtreleri Temizle</v-btn
            >
          </v-col>
          <v-col cols="auto">
            <v-btn color="primary" @click="fetchData">Ara</v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Ortalama Maaş Kartı -->
    <v-card class="pa-4 mb-4" v-if="averageSalary !== null">
      <v-card-title>Ortalama Maaş</v-card-title>
      <v-card-text>
        {{ averageSalary.toFixed(2) }} {{ filters.currency || "TL" }}
      </v-card-text>
    </v-card>

    <!-- Maaş Aralığı Özet Listesi -->
    <v-card class="pa-4">
      <v-card-title>Maaş Aralığı Özet (Gruplar)</v-card-title>
      <v-list dense>
        <v-list-item v-for="(item, index) in payRangeSummary" :key="index">
          <v-list-item-content>
            <v-list-item-title>
              {{ item.pay_range }} : {{ item.count }} adet
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { getSalaries, getPayRangeSummary } from "@/services/salaryService";

// Başlangıç filtre değerleri (range slider'lar için başlangıç aralığı belirleniyor)
const initialFilters = {
  title: "",
  currency: "",
  work_area: "",
  companySizeRange: [0, 1000], // Şirket büyüklüğü aralığı
  experienceRange: [0, 50], // Tecrübe aralığı (yıl)
  area: "",
};

const filters = ref({ ...initialFilters });

// Select box seçenekleri
const titleOptions = ["Jr", "Mid", "Senior", "Alex :D", "Guru"];
const currencyOptions = [
  "TL",
  "Dolar",
  "Euro",
  "SEK",
  "Sterlin",
  "Kuveyt dinarı",
];
const workAreaOptions = [
  "Full Stack Developer",
  "Backend Developer",
  "AI Engineer",
  "BI Developer",
  "DevOps Engineer",
  "Bilgi İşlem Uzmanı",
  "Big Data Engineer",
  "Yazılım Destek Uzmanı",
  "SAP Modul Danışmanı",
  "Site Reliability Engineer (SRE)",
  "Business Analyst",
  "Data Scientist",
  "Automation Engineer",
  "Android Developer",
  "Cloud Engineer",
  "Cyber Security Analyst",
  "Data Engineer",
  "Data Analyst",
  "Database Administrator (DBA)",
  "Embedded Software Developer",
  "Frontend Developer",
  "Game Developer",
  "Mobile Developer",
  "Machine Learning Engineer",
  "Product Manager",
  "Network Engineer",
  "Project Manager",
  "QA Engineer",
  "Software Architect",
  "Test Automation Engineer",
];

const salaries = ref([]);
const payRangeSummary = ref([]);

// Computed: En yüksek sayıya sahip maaş aralığından ortalama maaşı hesapla
const averageSalary = computed(() => {
  if (payRangeSummary.value.length === 0) return null;
  const maxGroup = payRangeSummary.value.reduce((prev, curr) => {
    return curr.count > prev.count ? curr : prev;
  });
  const range = maxGroup.pay_range;
  if (range && range.includes("-")) {
    const parts = range.split("-");
    const low = parseFloat(parts[0]);
    const high = parseFloat(parts[1]);
    if (!isNaN(low) && !isNaN(high)) {
      return (low + high) / 2;
    }
  } else if (range) {
    const num = parseFloat(range);
    if (!isNaN(num)) return num;
  }
  return null;
});

// Filtre nesnesini temizleyen yardımcı fonksiyon: boş string olan alanları çıkartır
function cleanFilters(filterObj) {
  return Object.fromEntries(
    Object.entries(filterObj).filter(([key, value]) => value !== "")
  );
}

// Range slider'ları API'ye uygun formatta dönüştürme:
// "companySizeRange" -> min_company_size, max_company_size
// "experienceRange" -> min_experience, max_experience
function transformFilters(filterObj) {
  const transformed = { ...filterObj };
  if (
    transformed.companySizeRange &&
    Array.isArray(transformed.companySizeRange)
  ) {
    transformed.min_company_size = transformed.companySizeRange[0];
    transformed.max_company_size = transformed.companySizeRange[1];
    delete transformed.companySizeRange;
  }
  if (
    transformed.experienceRange &&
    Array.isArray(transformed.experienceRange)
  ) {
    transformed.min_experience = transformed.experienceRange[0];
    transformed.max_experience = transformed.experienceRange[1];
    delete transformed.experienceRange;
  }
  return transformed;
}

async function fetchData() {
  try {
    const transformedFilters = transformFilters(filters.value);
    const cleanedFilters = cleanFilters(transformedFilters);
    // API çağrıları
    // const salaryData = await getSalaries(cleanedFilters);
    // salaries.value = salaryData;
    const summaryData = await getPayRangeSummary(cleanedFilters);
    payRangeSummary.value = summaryData;
  } catch (error) {
    console.error("API isteği sırasında hata:", error);
  }
}

// Filtreleri temizleyen fonksiyon
function clearFilters() {
  filters.value = { ...initialFilters };
  fetchData();
}
</script>

<style scoped>
.mb-4 {
  margin-bottom: 1rem;
}
</style>
