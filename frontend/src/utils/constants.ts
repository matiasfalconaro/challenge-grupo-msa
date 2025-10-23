/**
 * Application constants
 */

/**
 * Predefined parties (Lista A through Lista J)
 */
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

/**
 * Tab identifiers
 */
export const TABS = {
  SUBMIT: 'submit',
  HISTORY: 'history',
  CALCULATE: 'calculate',
  CLEAR: 'clear'
} as const;

/**
 * Tab type - union of all valid tab values
 */
export type TabType = typeof TABS[keyof typeof TABS];

/**
 * Form actions
 */
export const FORM_ACTIONS = {
  SUBMIT_VOTES: 'submit-votes',
  CALCULATE_AGGREGATE: 'calculate-aggregate',
  CLEAR_SUBMISSIONS: 'clear-submissions'
} as const;
