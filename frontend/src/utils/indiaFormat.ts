/**
 * Crime Compass 🧭 — Indian Localization & Formatting Utilities
 *
 * Provides:
 * 1. Indian number formatting (e.g., 2,20,663 and 1,00,000).
 * 2. INR currency formatting with ₹ symbol and lakh/crore terminology where helpful.
 * 3. Strict preservation of historical reference currency ($ USD) without fake rupee conversion.
 * 4. Indian date formatting: DD-MM-YYYY or DD MMM YYYY.
 * 5. Indian Standard Time (IST, UTC+05:30) with explicit timezone tagging.
 * 6. Re-export of comprehensive Indian administrative divisions (all 28 states, 8 UTs).
 */

import {
  INDIAN_ADMINISTRATIVE_DIVISIONS,
  getAllIndianStatesAndUTs,
  getDistrictsForStateOrUT,
  UNKNOWN_LOCATION_OPTION,
  OTHER_LOCATION_OPTION
} from '../data/indianLocations';

export {
  INDIAN_ADMINISTRATIVE_DIVISIONS,
  getAllIndianStatesAndUTs,
  getDistrictsForStateOrUT,
  UNKNOWN_LOCATION_OPTION,
  OTHER_LOCATION_OPTION
};

export const INDIAN_STATES_AND_UTS = getAllIndianStatesAndUTs();

export const DEFAULT_INDIAN_TIMEZONE = 'Asia/Kolkata';
export const IST_LABEL = 'IST (UTC+05:30)';
export const HISTORICAL_US_TIMEZONE_LABEL = 'US Central (CDT, UTC-05:00)';

/**
 * Formats numbers into the Indian numbering system (e.g. 2,20,663 instead of 220,663)
 */
export function formatIndianNumber(num: number | null | undefined): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '0';
  }
  return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Formats currency values:
 * - INR: ₹ 1,25,000 (with optional lakh/crore words for large amounts)
 * - USD: $ 1,500 (USD - Historical Reference) - Preserves original historical reference dataset currency without fake conversion
 */
export function formatCurrency(
  amount: number | null | undefined,
  currency: 'INR' | 'USD' | string = 'INR',
  showWords: boolean = false
): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return currency === 'INR' ? '₹0' : '$0 (USD - Historical Reference)';
  }

  if (currency === 'INR') {
    const formatted = new Intl.NumberFormat('en-IN', {
      maximumFractionDigits: 0,
    }).format(amount);

    if (showWords) {
      if (amount >= 10000000) {
        const crores = (amount / 10000000).toFixed(2);
        return `₹${formatted} (${crores} Crore)`;
      } else if (amount >= 100000) {
        const lakhs = (amount / 100000).toFixed(2);
        return `₹${formatted} (${lakhs} Lakh)`;
      }
    }
    return `₹${formatted}`;
  }

  // Preserve historical foreign currency without converting or mislabeling
  const formattedUsd = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(amount);
  return `$${formattedUsd} (USD - US Historical Reference)`;
}

/**
 * Formats dates to standard Indian format: DD-MM-YYYY or DD MMM YYYY
 */
export function formatIndianDate(
  dateInput: string | Date | null | undefined,
  style: 'numeric' | 'verbal' = 'numeric'
): string {
  if (!dateInput) return '—';

  try {
    let d: Date;
    if (typeof dateInput === 'string') {
      const parts = dateInput.split('T')[0].split('-');
      if (parts.length === 3) {
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const day = parseInt(parts[2], 10);
        if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
          if (style === 'verbal') {
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return `${String(day).padStart(2, '0')} ${months[month - 1]} ${year}`;
          }
          const dd = String(day).padStart(2, '0');
          const mm = String(month).padStart(2, '0');
          return `${dd}-${mm}-${year}`;
        }
      }
      d = new Date(dateInput);
    } else {
      d = dateInput;
    }

    if (isNaN(d.getTime())) return String(dateInput);

    const day = String(d.getDate()).padStart(2, '0');
    if (style === 'verbal') {
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return `${day} ${months[d.getMonth()]} ${d.getFullYear()}`;
    }
    const month = String(d.getMonth() + 1).padStart(2, '0');
    return `${day}-${month}-${d.getFullYear()}`;
  } catch {
    return String(dateInput);
  }
}

/**
 * Formats time with Indian Standard Time indicator
 */
export function formatIndianTime(
  timeStr: string | null | undefined,
  use24Hour: boolean = false,
  includeTimezone: boolean = false
): string {
  if (!timeStr) return '—';

  let formatted = timeStr;
  if (!/am|pm/i.test(timeStr)) {
    const parts = timeStr.trim().split(':');
    if (parts.length >= 2) {
      const hour = parseInt(parts[0], 10);
      const min = parseInt(parts[1], 10);
      if (!isNaN(hour) && !isNaN(min)) {
        if (use24Hour) {
          formatted = `${String(hour).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
        } else {
          const period = hour >= 12 ? 'PM' : 'AM';
          const displayHour = hour % 12 === 0 ? 12 : hour % 12;
          formatted = `${String(displayHour).padStart(2, '0')}:${String(min).padStart(2, '0')} ${period}`;
        }
      }
    }
  }

  return includeTimezone ? `${formatted} IST` : formatted;
}
