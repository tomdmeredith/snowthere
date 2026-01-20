// Quiz types and data structures for Snow Match Quiz

export type AgeRange = '0-3' | '4-7' | '8-12' | '13+' | 'mix'
export type SkillLevel = 'bunny' | 'blue' | 'black' | 'mix'
export type BudgetTier = 'value' | 'mid' | 'luxury'
export type TravelStyle = 'quick' | 'epic' | 'chill'
export type VibeType = 'village' | 'party' | 'family' | 'hidden'
export type Month = 'dec' | 'jan' | 'feb' | 'mar' | 'apr' | 'flexible'

export type MustHave =
  | 'ski-school'
  | 'ski-in-out'
  | 'nightlife'
  | 'non-ski'
  | 'english'
  | 'budget'
  | 'snow-guarantee'

export interface QuizOption {
  id: string
  emoji: string
  label: string
  description?: string
  color: string
}

export interface QuizQuestion {
  id: string
  step: number
  title: string
  subtitle?: string
  type: 'single' | 'multi'
  maxSelections?: number // For multi-select questions
  options: QuizOption[]
}

export interface QuizAnswers {
  ages: AgeRange | null
  skill: SkillLevel | null
  budget: BudgetTier | null
  travelStyle: TravelStyle | null
  mustHaves: MustHave[]
  vibe: VibeType | null
  timing: Month | null
}

export type PersonalityType =
  | 'adventure-seeker'
  | 'snow-bunny'
  | 'value-hunter'
  | 'village-lover'
  | 'family-first'
  | 'apres-enthusiast'

export interface PersonalityProfile {
  type: PersonalityType
  emoji: string
  title: string
  tagline: string
  description: string
  traits: string[]
  color: string
}

export interface ResortMatch {
  id: string
  name: string
  country: string
  region: string
  matchScore: number
  matchReason: string
  familyScore: number
  bestAgeMin: number
  bestAgeMax: number
  priceLevel: string
  slug: string
}

export interface QuizResult {
  personality: PersonalityProfile
  topMatches: ResortMatch[]
  answers: QuizAnswers
}
