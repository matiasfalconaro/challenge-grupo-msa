export const PREDEFINED_PARTIES = [
  'Lista A',
  'Lista B',
  'Lista C',
  'Lista D',
  'Lista E',
  'Lista F',
  'Lista G',
  'Lista H',
  'Lista I',
  'Lista J'
] as const;

export const TABS = {
  SUBMIT: 'submit',
  HISTORY: 'history',
  CALCULATE: 'calculate',
  CLEAR: 'clear'
} as const;

export type TabType = typeof TABS[keyof typeof TABS];

export const FORM_ACTIONS = {
  SUBMIT_VOTES: 'submit-votes',
  CALCULATE_AGGREGATE: 'calculate-aggregate',
  CLEAR_SUBMISSIONS: 'clear-submissions'
} as const;
