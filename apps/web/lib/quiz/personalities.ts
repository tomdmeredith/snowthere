// Personality type profiles for Snow Match Quiz
import { PersonalityProfile, PersonalityType } from './types'

export const PERSONALITY_PROFILES: Record<PersonalityType, PersonalityProfile> = {
  'adventure-seeker': {
    type: 'adventure-seeker',
    emoji: '🦅',
    title: 'Adventure Seekers',
    tagline: 'Go big or go home!',
    description:
      "Your family thrives on challenge and variety. You're not afraid to tackle black diamonds, and you love discovering new terrain. The bigger the mountain, the bigger your smiles.",
    traits: [
      'Love challenging terrain',
      'Seek variety and exploration',
      'Confident on steep slopes',
      'Value extensive trail networks',
    ],
    color: '#FF6B6B', // coral (decorative)
    colorDark: '#C92A2A', // dark coral for text (WCAG AA compliant)
  },
  'snow-bunny': {
    type: 'snow-bunny',
    emoji: '🐰',
    title: 'Snow Bunnies',
    tagline: 'Every expert was once a beginner',
    description:
      "You prioritize gentle learning and patience. Your kids will build confidence at their own pace, with plenty of hot chocolate breaks in between. The journey matters more than the summit.",
    traits: [
      'Focus on gentle learning',
      'Value excellent ski schools',
      'Appreciate beginner-friendly terrain',
      'Love cozy lodge breaks',
    ],
    color: '#FFE066', // gold (decorative)
    colorDark: '#996600', // dark gold for text (WCAG AA compliant)
  },
  'value-hunter': {
    type: 'value-hunter',
    emoji: '💰',
    title: 'Value Hunters',
    tagline: 'Smart spending, maximum skiing',
    description:
      "You know the best slopes aren't always the priciest. You've done your homework and know that amazing family ski trips don't have to break the bank. European gems? Yes please!",
    traits: [
      'Budget-conscious decisions',
      'Seek hidden gem resorts',
      'Love international value',
      'Smart about pass deals',
    ],
    color: '#4ECDC4', // teal (decorative)
    colorDark: '#1A7A73', // dark teal for text (WCAG AA compliant)
  },
  'village-lover': {
    type: 'village-lover',
    emoji: '🏔️',
    title: 'Village Lovers',
    tagline: 'Charm over everything',
    description:
      "For you, skiing is as much about the experience as the slopes. Cobblestone streets, cozy cafes, and that magical Alpine atmosphere are non-negotiable. The village IS the vacation.",
    traits: [
      'Value traditional atmosphere',
      'Love walkable villages',
      'Appreciate local culture',
      'Seek authentic experiences',
    ],
    color: '#95E1D3', // mint (decorative)
    colorDark: '#1A7A73', // dark teal for text (WCAG AA compliant)
  },
  'family-first': {
    type: 'family-first',
    emoji: '👨‍👩‍👧',
    title: 'Family First',
    tagline: 'Happy kids, happy life',
    description:
      "Everything centers around what works for the whole crew. From ski school quality to kid-friendly restaurants, you need a resort that truly understands families. Convenience is king.",
    traits: [
      'Prioritize kid amenities',
      'Value convenience',
      'Need flexible options',
      'Appreciate family packages',
    ],
    color: '#FFE066', // gold (decorative)
    colorDark: '#996600', // dark gold for text (WCAG AA compliant)
  },
  'apres-enthusiast': {
    type: 'apres-enthusiast',
    emoji: '🎉',
    title: 'Après Enthusiasts',
    tagline: 'The party starts at 3pm',
    description:
      "Sure, the skiing is great - but let's be honest, you live for the après! Live music, umbrella bars, and dancing in ski boots are essential ingredients for your perfect ski trip.",
    traits: [
      'Love lively atmosphere',
      'Seek social scenes',
      'Enjoy nightlife options',
      'Value mountain restaurants',
    ],
    color: '#FF6B6B', // coral (decorative)
    colorDark: '#C92A2A', // dark coral for text (WCAG AA compliant)
  },
}

export function getPersonalityProfile(type: PersonalityType): PersonalityProfile {
  return PERSONALITY_PROFILES[type]
}

export function getAllPersonalityTypes(): PersonalityType[] {
  return Object.keys(PERSONALITY_PROFILES) as PersonalityType[]
}
