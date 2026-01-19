export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      resorts: {
        Row: {
          id: string
          slug: string
          name: string
          country: string
          region: string
          latitude: number | null
          longitude: number | null
          status: 'draft' | 'published' | 'archived'
          created_at: string
          updated_at: string
          last_refreshed: string | null
          trail_map_data: Json | null
        }
        Insert: {
          id?: string
          slug: string
          name: string
          country: string
          region: string
          latitude?: number | null
          longitude?: number | null
          status?: 'draft' | 'published' | 'archived'
          created_at?: string
          updated_at?: string
          last_refreshed?: string | null
          trail_map_data?: Json | null
        }
        Update: {
          id?: string
          slug?: string
          name?: string
          country?: string
          region?: string
          latitude?: number | null
          longitude?: number | null
          status?: 'draft' | 'published' | 'archived'
          created_at?: string
          updated_at?: string
          last_refreshed?: string | null
          trail_map_data?: Json | null
        }
      }
      resort_family_metrics: {
        Row: {
          resort_id: string
          family_overall_score: number | null
          best_age_min: number | null
          best_age_max: number | null
          kid_friendly_terrain_pct: number | null
          has_childcare: boolean | null
          childcare_min_age: number | null
          ski_school_min_age: number | null
          kids_ski_free_age: number | null
          has_magic_carpet: boolean | null
          has_terrain_park_kids: boolean | null
          perfect_if: string[] | null
          skip_if: string[] | null
        }
        Insert: {
          resort_id: string
          family_overall_score?: number | null
          best_age_min?: number | null
          best_age_max?: number | null
          kid_friendly_terrain_pct?: number | null
          has_childcare?: boolean | null
          childcare_min_age?: number | null
          ski_school_min_age?: number | null
          kids_ski_free_age?: number | null
          has_magic_carpet?: boolean | null
          has_terrain_park_kids?: boolean | null
          perfect_if?: string[] | null
          skip_if?: string[] | null
        }
        Update: {
          resort_id?: string
          family_overall_score?: number | null
          best_age_min?: number | null
          best_age_max?: number | null
          kid_friendly_terrain_pct?: number | null
          has_childcare?: boolean | null
          childcare_min_age?: number | null
          ski_school_min_age?: number | null
          kids_ski_free_age?: number | null
          has_magic_carpet?: boolean | null
          has_terrain_park_kids?: boolean | null
          perfect_if?: string[] | null
          skip_if?: string[] | null
        }
      }
      resort_content: {
        Row: {
          resort_id: string
          quick_take: string | null
          getting_there: string | null
          where_to_stay: string | null
          lift_tickets: string | null
          on_mountain: string | null
          off_mountain: string | null
          parent_reviews_summary: string | null
          faqs: Json | null
          llms_txt: string | null
          seo_meta: Json | null
          content_version: number
        }
        Insert: {
          resort_id: string
          quick_take?: string | null
          getting_there?: string | null
          where_to_stay?: string | null
          lift_tickets?: string | null
          on_mountain?: string | null
          off_mountain?: string | null
          parent_reviews_summary?: string | null
          faqs?: Json | null
          llms_txt?: string | null
          seo_meta?: Json | null
          content_version?: number
        }
        Update: {
          resort_id?: string
          quick_take?: string | null
          getting_there?: string | null
          where_to_stay?: string | null
          lift_tickets?: string | null
          on_mountain?: string | null
          off_mountain?: string | null
          parent_reviews_summary?: string | null
          faqs?: Json | null
          llms_txt?: string | null
          seo_meta?: Json | null
          content_version?: number
        }
      }
      resort_costs: {
        Row: {
          resort_id: string
          currency: string
          lift_adult_daily: number | null
          lift_child_daily: number | null
          lift_family_daily: number | null
          lodging_budget_nightly: number | null
          lodging_mid_nightly: number | null
          lodging_luxury_nightly: number | null
          meal_family_avg: number | null
          estimated_family_daily: number | null
        }
        Insert: {
          resort_id: string
          currency?: string
          lift_adult_daily?: number | null
          lift_child_daily?: number | null
          lift_family_daily?: number | null
          lodging_budget_nightly?: number | null
          lodging_mid_nightly?: number | null
          lodging_luxury_nightly?: number | null
          meal_family_avg?: number | null
          estimated_family_daily?: number | null
        }
        Update: {
          resort_id?: string
          currency?: string
          lift_adult_daily?: number | null
          lift_child_daily?: number | null
          lift_family_daily?: number | null
          lodging_budget_nightly?: number | null
          lodging_mid_nightly?: number | null
          lodging_luxury_nightly?: number | null
          meal_family_avg?: number | null
          estimated_family_daily?: number | null
        }
      }
      ski_quality_calendar: {
        Row: {
          id: string
          resort_id: string
          month: number
          snow_quality_score: number | null
          crowd_level: 'low' | 'medium' | 'high' | null
          family_recommendation: number | null
          notes: string | null
        }
        Insert: {
          id?: string
          resort_id: string
          month: number
          snow_quality_score?: number | null
          crowd_level?: 'low' | 'medium' | 'high' | null
          family_recommendation?: number | null
          notes?: string | null
        }
        Update: {
          id?: string
          resort_id?: string
          month?: number
          snow_quality_score?: number | null
          crowd_level?: 'low' | 'medium' | 'high' | null
          family_recommendation?: number | null
          notes?: string | null
        }
      }
      ski_passes: {
        Row: {
          id: string
          name: string
          type: string | null
          website_url: string | null
          purchase_url: string | null
        }
        Insert: {
          id?: string
          name: string
          type?: string | null
          website_url?: string | null
          purchase_url?: string | null
        }
        Update: {
          id?: string
          name?: string
          type?: string | null
          website_url?: string | null
          purchase_url?: string | null
        }
      }
      resort_passes: {
        Row: {
          resort_id: string
          pass_id: string
          access_type: string | null
        }
        Insert: {
          resort_id: string
          pass_id: string
          access_type?: string | null
        }
        Update: {
          resort_id?: string
          pass_id?: string
          access_type?: string | null
        }
      }
      content_queue: {
        Row: {
          id: string
          resort_id: string | null
          task_type: string
          status: 'pending' | 'processing' | 'completed' | 'failed'
          priority: number
          attempts: number
          last_error: string | null
          created_at: string
          started_at: string | null
          completed_at: string | null
        }
        Insert: {
          id?: string
          resort_id?: string | null
          task_type: string
          status?: 'pending' | 'processing' | 'completed' | 'failed'
          priority?: number
          attempts?: number
          last_error?: string | null
          created_at?: string
          started_at?: string | null
          completed_at?: string | null
        }
        Update: {
          id?: string
          resort_id?: string | null
          task_type?: string
          status?: 'pending' | 'processing' | 'completed' | 'failed'
          priority?: number
          attempts?: number
          last_error?: string | null
          created_at?: string
          started_at?: string | null
          completed_at?: string | null
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}

// Convenience types
export type Resort = Database['public']['Tables']['resorts']['Row']
export type ResortFamilyMetrics = Database['public']['Tables']['resort_family_metrics']['Row']
export type ResortContent = Database['public']['Tables']['resort_content']['Row']
export type ResortCosts = Database['public']['Tables']['resort_costs']['Row']
export type SkiQualityCalendar = Database['public']['Tables']['ski_quality_calendar']['Row']
export type SkiPass = Database['public']['Tables']['ski_passes']['Row']

// Full resort with all relations
export interface ResortWithDetails extends Resort {
  family_metrics: ResortFamilyMetrics | null
  content: ResortContent | null
  costs: ResortCosts | null
  calendar: SkiQualityCalendar[]
  passes: (SkiPass & { access_type: string | null })[]
}
