/**
 * Crime Compass 🧭 — Indian Localization & Formatting Utilities
 *
 * Provides:
 * 1. Indian number formatting (e.g., 2,20,663 and 1,00,000).
 * 2. INR currency formatting with ₹ symbol and clear separation of foreign currencies.
 * 3. Indian date formatting: DD/MM/YYYY.
 * 4. Indian time formatting: 12-hour format with AM/PM (optional 24-hour).
 * 5. Comprehensive list of 28 Indian States and 8 Union Territories.
 * 6. Asia/Kolkata timezone constants for user-entered incidents.
 */

export const DEFAULT_INDIAN_TIMEZONE = 'Asia/Kolkata';

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
 * - INR: ₹ 1,50,000
 * - USD: $ 1,500 (USD) - Preserves original historical reference dataset currency
 */
export function formatCurrency(
  amount: number | null | undefined,
  currency: 'INR' | 'USD' = 'INR'
): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return currency === 'INR' ? '₹0' : '$0 (USD)';
  }

  if (currency === 'INR') {
    const formatted = new Intl.NumberFormat('en-IN', {
      maximumFractionDigits: 0,
    }).format(amount);
    return `₹${formatted}`;
  }

  // Preserve historical foreign currency without converting or mislabeling
  const formattedUsd = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(amount);
  return `$${formattedUsd} (USD)`;
}

/**
 * Formats dates to standard Indian format: DD/MM/YYYY
 */
export function formatIndianDate(dateInput: string | Date | null | undefined): string {
  if (!dateInput) return '—';

  try {
    let d: Date;
    if (typeof dateInput === 'string') {
      // Handle standard YYYY-MM-DD
      const parts = dateInput.split('T')[0].split('-');
      if (parts.length === 3) {
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const day = parseInt(parts[2], 10);
        if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
          const dd = String(day).padStart(2, '0');
          const mm = String(month).padStart(2, '0');
          const yyyy = String(year);
          return `${dd}/${mm}/${yyyy}`;
        }
      }
      d = new Date(dateInput);
    } else {
      d = dateInput;
    }

    if (isNaN(d.getTime())) return String(dateInput);

    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
  } catch {
    return String(dateInput);
  }
}

/**
 * Formats time to 12-hour AM/PM format (default for Indian English) or 24-hour if requested.
 */
export function formatIndianTime(timeStr: string | null | undefined, use24Hour: boolean = false): string {
  if (!timeStr) return '—';

  // If already in AM/PM format
  if (/am|pm/i.test(timeStr)) return timeStr;

  const parts = timeStr.trim().split(':');
  if (parts.length < 2) return timeStr;

  const hour = parseInt(parts[0], 10);
  const min = parseInt(parts[1], 10);

  if (isNaN(hour) || isNaN(min)) return timeStr;

  if (use24Hour) {
    return `${String(hour).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
  }

  const period = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 === 0 ? 12 : hour % 12;
  return `${String(displayHour).padStart(2, '0')}:${String(min).padStart(2, '0')} ${period}`;
}

/**
 * All 28 Indian States & 8 Union Territories
 */
export const INDIAN_STATES_AND_UTS = [
  // 28 States
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  // 8 Union Territories
  'Andaman and Nicobar Islands',
  'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi (NCT)',
  'Jammu and Kashmir',
  'Ladakh',
  'Lakshadweep',
  'Puducherry'
];

/**
 * Major Indian districts/cities for quick selection
 */
export const POPULAR_INDIAN_DISTRICTS: Record<string, string[]> = {
  'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Thane', 'Nashik', 'Aurangabad', 'Solapur'],
  'Delhi (NCT)': ['New Delhi', 'North Delhi', 'South Delhi', 'East Delhi', 'West Delhi', 'Central Delhi'],
  'Karnataka': ['Bengaluru Urban', 'Bengaluru Rural', 'Mysuru', 'Mangaluru', 'Hubballi-Dharwad', 'Belagavi'],
  'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli'],
  'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi', 'Noida / Gautam Buddha Nagar', 'Ghaziabad', 'Agra', 'Prayagraj'],
  'Telangana': ['Hyderabad', 'Secunderabad', 'Warangal', 'Nizamabad', 'Karimnagar'],
  'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Gandhinagar'],
  'West Bengal': ['Kolkata', 'Howrah', 'North 24 Parganas', 'South 24 Parganas', 'Darjeeling', 'Siliguri'],
  'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Ajmer', 'Bikaner'],
  'Kerala': ['Thiruvananthapuram', 'Kochi / Ernakulam', 'Kozhikode', 'Thrissur', 'Kollam'],
  'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali']
};
