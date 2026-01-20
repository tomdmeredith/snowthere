// Scoring algorithm for Snow Match Quiz
import {
  QuizAnswers,
  PersonalityType,
  ResortMatch,
  QuizResult,
  AgeRange,
  SkillLevel,
  BudgetTier,
  VibeType,
  MustHave,
} from './types'
import { getPersonalityProfile } from './personalities'

// Age range boundaries
const AGE_BOUNDS: Record<string, { min: number; max: number }> = {
  '0-3': { min: 0, max: 3 },
  '4-7': { min: 4, max: 7 },
  '8-12': { min: 8, max: 12 },
  '13+': { min: 13, max: 18 },
  'mix': { min: 0, max: 18 },
}

// Budget tier mapping to price levels
const BUDGET_MAP: Record<BudgetTier, string[]> = {
  value: ['$', '$$'],
  mid: ['$$', '$$$'],
  luxury: ['$$$', '$$$$'],
}

// Determine personality type based on quiz answers
export function determinePersonality(answers: QuizAnswers): PersonalityType {
  const scores: Record<PersonalityType, number> = {
    'adventure-seeker': 0,
    'snow-bunny': 0,
    'value-hunter': 0,
    'village-lover': 0,
    'family-first': 0,
    'apres-enthusiast': 0,
  }

  // Skill level influences
  if (answers.skill === 'black') {
    scores['adventure-seeker'] += 3
  } else if (answers.skill === 'bunny') {
    scores['snow-bunny'] += 3
    scores['family-first'] += 1
  } else if (answers.skill === 'mix') {
    scores['family-first'] += 2
  }

  // Budget influences
  if (answers.budget === 'value') {
    scores['value-hunter'] += 3
  } else if (answers.budget === 'luxury') {
    scores['apres-enthusiast'] += 1
    scores['village-lover'] += 1
  }

  // Vibe influences
  if (answers.vibe === 'village') {
    scores['village-lover'] += 3
  } else if (answers.vibe === 'party') {
    scores['apres-enthusiast'] += 3
  } else if (answers.vibe === 'family') {
    scores['family-first'] += 3
    scores['snow-bunny'] += 1
  } else if (answers.vibe === 'hidden') {
    scores['adventure-seeker'] += 2
    scores['value-hunter'] += 2
  }

  // Must-haves influences
  if (answers.mustHaves.includes('ski-school')) {
    scores['snow-bunny'] += 2
    scores['family-first'] += 2
  }
  if (answers.mustHaves.includes('nightlife')) {
    scores['apres-enthusiast'] += 3
  }
  if (answers.mustHaves.includes('non-ski')) {
    scores['family-first'] += 1
    scores['village-lover'] += 1
  }
  if (answers.mustHaves.includes('budget')) {
    scores['value-hunter'] += 2
  }

  // Travel style influences
  if (answers.travelStyle === 'epic') {
    scores['adventure-seeker'] += 2
    scores['village-lover'] += 1
  } else if (answers.travelStyle === 'chill') {
    scores['family-first'] += 1
    scores['snow-bunny'] += 1
  }

  // Ages influence (young kids = family-first, teens = adventure)
  if (answers.ages === '0-3' || answers.ages === '4-7') {
    scores['family-first'] += 2
    scores['snow-bunny'] += 1
  } else if (answers.ages === '13+') {
    scores['adventure-seeker'] += 1
    scores['apres-enthusiast'] += 1
  }

  // Find the highest scoring personality
  let maxScore = 0
  let personality: PersonalityType = 'family-first'

  for (const [type, score] of Object.entries(scores)) {
    if (score > maxScore) {
      maxScore = score
      personality = type as PersonalityType
    }
  }

  return personality
}

// Calculate match score for a resort based on quiz answers
export function calculateResortMatchScore(
  resort: {
    id: string
    name: string
    country: string
    region: string
    familyScore: number
    bestAgeMin: number
    bestAgeMax: number
    priceLevel: string
    hasSkiSchool?: boolean
    hasSkiInOut?: boolean
    nightlifeScore?: number
    nonSkiActivities?: number
    englishFriendly?: boolean
    snowReliability?: number
    beginnerTerrain?: number
    advancedTerrain?: number
    villageCharm?: number
    slug: string
  },
  answers: QuizAnswers
): number {
  let score = 0
  const weights = {
    ageMatch: 0.25,
    budgetMatch: 0.2,
    mustHaves: 0.25,
    vibeMatch: 0.15,
    skillMatch: 0.15,
  }

  // Age match (25%)
  if (answers.ages) {
    const ageBounds = AGE_BOUNDS[answers.ages]
    if (ageBounds) {
      // Check if resort's best age range overlaps with user's kids
      const overlap =
        resort.bestAgeMin <= ageBounds.max && resort.bestAgeMax >= ageBounds.min
      if (overlap) {
        // Calculate how well the ranges overlap
        const overlapMin = Math.max(resort.bestAgeMin, ageBounds.min)
        const overlapMax = Math.min(resort.bestAgeMax, ageBounds.max)
        const overlapSize = overlapMax - overlapMin
        const rangeSize = ageBounds.max - ageBounds.min
        score += weights.ageMatch * Math.min(1, (overlapSize / rangeSize) * 1.5)
      }
    }
  }

  // Budget match (20%)
  if (answers.budget) {
    const acceptablePriceLevels = BUDGET_MAP[answers.budget]
    if (acceptablePriceLevels.includes(resort.priceLevel)) {
      score += weights.budgetMatch
    } else if (
      // Adjacent budget tier gets partial credit
      (answers.budget === 'value' && resort.priceLevel === '$$$') ||
      (answers.budget === 'luxury' && resort.priceLevel === '$$')
    ) {
      score += weights.budgetMatch * 0.5
    }
  }

  // Must-haves match (25%)
  if (answers.mustHaves.length > 0) {
    let mustHaveScore = 0
    const mustHaveChecks: Record<MustHave, boolean> = {
      'ski-school': resort.hasSkiSchool ?? resort.familyScore > 7,
      'ski-in-out': resort.hasSkiInOut ?? false,
      'nightlife': (resort.nightlifeScore ?? 0) >= 7,
      'non-ski': (resort.nonSkiActivities ?? 0) >= 5,
      'english': resort.englishFriendly ?? true,
      'budget': ['$', '$$'].includes(resort.priceLevel),
      'snow-guarantee': (resort.snowReliability ?? 0) >= 8,
    }

    for (const mustHave of answers.mustHaves) {
      if (mustHaveChecks[mustHave]) {
        mustHaveScore += 1 / answers.mustHaves.length
      }
    }
    score += weights.mustHaves * mustHaveScore
  } else {
    // No must-haves = full credit
    score += weights.mustHaves
  }

  // Vibe match (15%)
  if (answers.vibe) {
    const vibeScores: Record<VibeType, number> = {
      village: resort.villageCharm ?? (resort.familyScore > 8 ? 8 : 6),
      party: resort.nightlifeScore ?? 5,
      family: resort.familyScore,
      hidden: resort.familyScore > 6 && resort.familyScore < 9 ? 8 : 5,
    }
    score += weights.vibeMatch * (vibeScores[answers.vibe] / 10)
  }

  // Skill match (15%)
  if (answers.skill) {
    const beginnerPct = resort.beginnerTerrain ?? 30
    const advancedPct = resort.advancedTerrain ?? 20
    const intermediatePct = 100 - beginnerPct - advancedPct

    switch (answers.skill) {
      case 'bunny':
        score += weights.skillMatch * Math.min(1, beginnerPct / 40)
        break
      case 'blue':
        // Intermediate wants balanced terrain
        score += weights.skillMatch * Math.min(1, intermediatePct / 50)
        break
      case 'black':
        score += weights.skillMatch * Math.min(1, advancedPct / 30)
        break
      case 'mix':
        // Mixed ability wants variety
        const variety =
          beginnerPct > 20 && advancedPct > 15 && intermediatePct > 30
        score += weights.skillMatch * (variety ? 1 : 0.7)
        break
    }
  }

  // Bonus for high family score (always relevant)
  score += (resort.familyScore / 10) * 0.1

  return Math.min(1, score) * 100
}

// Generate match reason text
export function generateMatchReason(
  resort: { name: string; familyScore: number; priceLevel: string },
  answers: QuizAnswers,
  matchScore: number
): string {
  const reasons: string[] = []

  if (matchScore >= 90) {
    reasons.push(`Nearly perfect for your family!`)
  } else if (matchScore >= 80) {
    reasons.push(`Great match for your crew`)
  } else {
    reasons.push(`Solid option for families like yours`)
  }

  if (answers.ages === '0-3' || answers.ages === '4-7') {
    if (resort.familyScore >= 8) {
      reasons.push(`excellent for young kids`)
    }
  }

  if (answers.budget === 'value' && ['$', '$$'].includes(resort.priceLevel)) {
    reasons.push(`amazing value`)
  }

  return reasons.join(' - ')
}

// Main function to compute quiz results
export function computeQuizResults(
  answers: QuizAnswers,
  resorts: Array<{
    id: string
    name: string
    country: string
    region: string
    familyScore: number
    bestAgeMin: number
    bestAgeMax: number
    priceLevel: string
    hasSkiSchool?: boolean
    hasSkiInOut?: boolean
    nightlifeScore?: number
    nonSkiActivities?: number
    englishFriendly?: boolean
    snowReliability?: number
    beginnerTerrain?: number
    advancedTerrain?: number
    villageCharm?: number
    slug: string
  }>
): QuizResult {
  // Determine personality type
  const personalityType = determinePersonality(answers)
  const personality = getPersonalityProfile(personalityType)

  // Score all resorts and get top matches
  const scoredResorts: ResortMatch[] = resorts
    .map((resort) => {
      const matchScore = calculateResortMatchScore(resort, answers)
      return {
        id: resort.id,
        name: resort.name,
        country: resort.country,
        region: resort.region,
        matchScore: Math.round(matchScore),
        matchReason: generateMatchReason(resort, answers, matchScore),
        familyScore: resort.familyScore,
        bestAgeMin: resort.bestAgeMin,
        bestAgeMax: resort.bestAgeMax,
        priceLevel: resort.priceLevel,
        slug: resort.slug,
      }
    })
    .sort((a, b) => b.matchScore - a.matchScore)

  // Return top 3 matches
  const topMatches = scoredResorts.slice(0, 3)

  return {
    personality,
    topMatches,
    answers,
  }
}

// Helper to get initial empty answers
export function getInitialAnswers(): QuizAnswers {
  return {
    ages: null,
    skill: null,
    budget: null,
    travelStyle: null,
    mustHaves: [],
    vibe: null,
    timing: null,
  }
}
