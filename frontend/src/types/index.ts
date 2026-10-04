/**
 * ALIMENTA GLOBAL — Core Domain Types
 * UNESCO-Affiliated Digital Commons Architecture
 */

export type NutriScoreGrade = 'a' | 'b' | 'c' | 'd' | 'e';
export type NovaGroup = 1 | 2 | 3 | 4;
export type EcoScoreGrade = 'a' | 'b' | 'c' | 'd' | 'e';

export interface ProductComposition {
  id: string;
  name: string;
  category: 'beverage' | 'dairy' | 'plant_based' | 'snack' | 'staple';
  subCategory: string;
  sugarPer100g: number;
  sugarCubesEquivalent: number; // 1 cube ~ 4g sugar
  caloriesPer100g: number;
  nutriScore: NutriScoreGrade;
  novaGroup: NovaGroup;
  ecoScore: EcoScoreGrade;
  additives: {
    code: string;
    name: string;
    riskLevel: 'safe' | 'moderate' | 'high_risk';
    function: string;
  }[];
  reformulationDeltaPercent?: number; // e.g., -15% sugar reduction since 2018
  barcode: string;
}

export interface CosmeticComposition {
  id: string;
  productName: string;
  brand: string;
  category: 'shampoo' | 'skincare' | 'toothpaste' | 'soap';
  chemicalAudit: {
    silicones: boolean;
    sulfates: boolean;
    endocrineDisruptors: boolean;
    microplastics: boolean;
    allergens: string[];
  };
  inciIngredients: string[];
  riskRating: 'optimal' | 'moderate' | 'caution' | 'hazardous';
}

export interface ReuseEntity {
  id: string;
  name: string;
  tagline: string;
  description: string;
  theme: 'nutrition' | 'environment' | 'shopping' | 'research' | 'health' | 'education' | 'general';
  tag?: string;
  project?: 'off' | 'obf' | 'opff' | 'opf';
  website: string;
  source_code_url?: string;
  ios_url?: string;
  android_url?: string;
  featured?: boolean;
  countries?: string[];
  installs?: number;
  contributed_products?: number;
}

export interface ScientificPublication {
  id: string;
  title: string;
  authors: string[];
  year: number;
  journal_or_conference?: string;
  doi?: string;
  url?: string;
  pdf_url?: string;
  abstract?: string;
  citations_count?: number;
  topics?: string[];
}

export interface ScanPartyWorkshop {
  id: string;
  title: string;
  type: 'upcoming' | 'past';
  status: 'upcoming' | 'completed' | 'cancelled';
  date: string;
  location: string;
  city: string;
  country: string;
  venue?: string;
  organizer?: string;
  scanned_products_count?: number;
  attendees_count?: number;
}

export interface GlobalTelemetryStats {
  totalBarcodes: number;
  activeContributors: number;
  ecosystemReuses: number;
  scientificPublications: number;
  scanParties: number;
  apiStatus: 'online' | 'degraded' | 'offline';
  uptimeSeconds: number;
}
