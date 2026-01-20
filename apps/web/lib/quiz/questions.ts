// Quiz questions data for Snow Match Quiz
import { QuizQuestion } from './types'

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 'ages',
    step: 1,
    title: "How old are your little shredders?",
    subtitle: "Select all that apply for your crew",
    type: 'single',
    options: [
      {
        id: '0-3',
        emoji: '👶',
        label: 'Tots',
        description: 'Under 4 - Snow angels & hot cocoa',
        color: '#FFE066', // gold
      },
      {
        id: '4-7',
        emoji: '🧒',
        label: 'Minis',
        description: '4-7 years - Pizza wedge pros',
        color: '#4ECDC4', // teal
      },
      {
        id: '8-12',
        emoji: '🧑',
        label: 'Riders',
        description: '8-12 years - Ready for adventure',
        color: '#FF6B6B', // coral
      },
      {
        id: '13+',
        emoji: '🧑‍🦱',
        label: 'Teens',
        description: '13+ - Let them loose!',
        color: '#95E1D3', // mint
      },
    ],
  },
  {
    id: 'skill',
    step: 2,
    title: "What's your family's slope style?",
    subtitle: "Think about your least experienced skier",
    type: 'single',
    options: [
      {
        id: 'bunny',
        emoji: '🐰',
        label: 'Bunny slopes',
        description: 'Just learning or need gentle terrain',
        color: '#FFE066',
      },
      {
        id: 'blue',
        emoji: '🎿',
        label: 'Blue cruisers',
        description: 'Comfortable on intermediate runs',
        color: '#4ECDC4',
      },
      {
        id: 'black',
        emoji: '⛷️',
        label: 'Black diamonds',
        description: 'Ready for challenging terrain',
        color: '#FF6B6B',
      },
      {
        id: 'mix',
        emoji: '🏔️',
        label: 'Mix it up',
        description: 'Different levels in our family',
        color: '#95E1D3',
      },
    ],
  },
  {
    id: 'budget',
    step: 3,
    title: "Budget vibes?",
    subtitle: "No judgment here - just finding your fit",
    type: 'single',
    options: [
      {
        id: 'value',
        emoji: '💰',
        label: 'Value',
        description: 'Smart spending, maximum skiing',
        color: '#4ECDC4',
      },
      {
        id: 'mid',
        emoji: '💰💰',
        label: 'Mid-range',
        description: 'Balance of comfort & cost',
        color: '#FFE066',
      },
      {
        id: 'luxury',
        emoji: '💰💰💰',
        label: 'Treat ourselves',
        description: 'This is our big vacation!',
        color: '#FF6B6B',
      },
    ],
  },
  {
    id: 'travelStyle',
    step: 4,
    title: "What's your travel style?",
    subtitle: "How long do you want to be away?",
    type: 'single',
    options: [
      {
        id: 'quick',
        emoji: '✈️',
        label: 'Quick getaway',
        description: '3-4 days - In and out',
        color: '#FF6B6B',
      },
      {
        id: 'epic',
        emoji: '🏔️',
        label: 'Epic adventure',
        description: '7+ days - Go big or go home',
        color: '#4ECDC4',
      },
      {
        id: 'chill',
        emoji: '🏡',
        label: 'Chill & cozy',
        description: '5-6 days - Just right',
        color: '#95E1D3',
      },
    ],
  },
  {
    id: 'mustHaves',
    step: 5,
    title: "Must-haves?",
    subtitle: "Pick up to 3 non-negotiables",
    type: 'multi',
    maxSelections: 3,
    options: [
      {
        id: 'ski-school',
        emoji: '👶',
        label: 'Ski school',
        description: 'Quality instruction for kids',
        color: '#FFE066',
      },
      {
        id: 'ski-in-out',
        emoji: '🏨',
        label: 'Ski-in/out',
        description: 'Walk to the lifts',
        color: '#4ECDC4',
      },
      {
        id: 'nightlife',
        emoji: '🎭',
        label: 'Nightlife',
        description: 'Après-ski scene',
        color: '#FF6B6B',
      },
      {
        id: 'non-ski',
        emoji: '🛷',
        label: 'Non-ski activities',
        description: 'For non-skiers or rest days',
        color: '#95E1D3',
      },
    ],
  },
  {
    id: 'vibe',
    step: 6,
    title: "What's the vibe?",
    subtitle: "What atmosphere are you dreaming of?",
    type: 'single',
    options: [
      {
        id: 'village',
        emoji: '🏔️',
        label: 'Charming village',
        description: 'Traditional Alpine feel',
        color: '#95E1D3',
      },
      {
        id: 'party',
        emoji: '🎉',
        label: 'Party scene',
        description: 'Lively après-ski energy',
        color: '#FF6B6B',
      },
      {
        id: 'family',
        emoji: '👨‍👩‍👧',
        label: 'Family-focused',
        description: 'Built for families like yours',
        color: '#FFE066',
      },
      {
        id: 'hidden',
        emoji: '🤫',
        label: 'Hidden gem',
        description: 'Off the beaten path',
        color: '#4ECDC4',
      },
    ],
  },
  {
    id: 'timing',
    step: 7,
    title: "When are you dreaming of going?",
    subtitle: "Peak times may affect availability",
    type: 'single',
    options: [
      {
        id: 'dec',
        emoji: '❄️',
        label: 'December',
        description: 'Holiday magic',
        color: '#4ECDC4',
      },
      {
        id: 'jan',
        emoji: '⛷️',
        label: 'January',
        description: 'Peak powder season',
        color: '#FFE066',
      },
      {
        id: 'feb',
        emoji: '🏔️',
        label: 'February',
        description: 'School break time',
        color: '#FF6B6B',
      },
      {
        id: 'mar',
        emoji: '🌸',
        label: 'March',
        description: 'Spring skiing',
        color: '#95E1D3',
      },
    ],
  },
]

export const TOTAL_STEPS = QUIZ_QUESTIONS.length
