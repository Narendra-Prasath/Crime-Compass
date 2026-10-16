import React, { useState, useMemo } from 'react';
import { MapPin, Search, Info, Check, HelpCircle } from 'lucide-react';
import {
  INDIAN_ADMINISTRATIVE_DIVISIONS,
  getAllIndianStatesAndUTs,
  getDistrictsForStateOrUT,
  UNKNOWN_LOCATION_OPTION,
  OTHER_LOCATION_OPTION
} from '../data/indianLocations';

interface IndianLocationSelectorProps {
  country?: string;
  stateUt?: string;
  district?: string;
  cityTown?: string;
  locality?: string;
  pinCode?: string;
  onChange: (fields: {
    country?: string;
    state_ut?: string;
    district?: string;
    city_town?: string;
    locality?: string;
    pin_code?: string;
  }) => void;
}

export const IndianLocationSelector: React.FC<IndianLocationSelectorProps> = ({
  country = 'India',
  stateUt = 'Karnataka',
  district = 'Bengaluru Urban',
  cityTown = 'Bengaluru',
  locality = 'Indiranagar',
  pinCode = '560038',
  onChange
}) => {
  const [districtSearch, setDistrictSearch] = useState('');
  const [stateSearch, setStateSearch] = useState('');
  const [showStateDropdown, setShowStateDropdown] = useState(false);
  const [showDistrictDropdown, setShowDistrictDropdown] = useState(false);

  const statesList = useMemo(() => {
    return [
      UNKNOWN_LOCATION_OPTION,
      ...getAllIndianStatesAndUTs(),
      OTHER_LOCATION_OPTION
    ];
  }, []);

  const filteredStates = useMemo(() => {
    if (!stateSearch.trim()) return statesList;
    const q = stateSearch.toLowerCase();
    return statesList.filter((s) => s.toLowerCase().includes(q));
  }, [stateSearch, statesList]);

  const districtsList = useMemo(() => {
    if (!stateUt || stateUt === UNKNOWN_LOCATION_OPTION) {
      return [UNKNOWN_LOCATION_OPTION, OTHER_LOCATION_OPTION];
    }
    return getDistrictsForStateOrUT(stateUt);
  }, [stateUt]);

  const filteredDistricts = useMemo(() => {
    if (!districtSearch.trim()) return districtsList;
    const q = districtSearch.toLowerCase();
    return districtsList.filter((d) => d.toLowerCase().includes(q));
  }, [districtSearch, districtsList]);

  const handleStateSelect = (val: string) => {
    setStateSearch('');
    setShowStateDropdown(false);
    const newDistricts = getDistrictsForStateOrUT(val);
    const defaultDistrict = newDistricts.length > 1 ? newDistricts[1] : UNKNOWN_LOCATION_OPTION;
    onChange({
      state_ut: val,
      district: val === UNKNOWN_LOCATION_OPTION ? UNKNOWN_LOCATION_OPTION : defaultDistrict
    });
  };

  const handleDistrictSelect = (val: string) => {
    setDistrictSearch('');
    setShowDistrictDropdown(false);
    onChange({ district: val });
  };

  const handlePinCodeChange = (raw: string) => {
    const cleaned = raw.replace(/\D/g, '').slice(0, 6);
    onChange({ pin_code: cleaned });
  };

  return (
    <div
      style={{
        background: 'var(--bg-subtle)',
        padding: '18px',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        marginTop: '12px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ fontSize: '0.86rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MapPin size={16} style={{ color: 'var(--accent-emerald)' }} />
          <span>Indian Geographic Location (28 States &bull; 8 Union Territories)</span>
        </div>
        <span
          style={{
            fontSize: '0.72rem',
            padding: '2px 8px',
            borderRadius: '4px',
            background: 'rgba(16, 185, 129, 0.15)',
            color: 'var(--accent-emerald)',
            border: '1px solid rgba(16, 185, 129, 0.3)'
          }}
        >
          Official LGD Hierarchy
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px' }}>
        {/* Country */}
        <div>
          <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '5px' }}>
            Jurisdiction Country
          </label>
          <select
            value={country || 'India'}
            onChange={(e) => {
              const c = e.target.value;
              if (c === 'India') {
                onChange({ country: 'India', state_ut: 'Karnataka', district: 'Bengaluru Urban' });
              } else {
                onChange({ country: c, state_ut: '', district: '' });
              }
            }}
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
              color: 'var(--text-main)',
              fontSize: '0.84rem'
            }}
          >
            <option value="India">India (IST / ₹ INR)</option>
            <option value="United States">United States (Historical Baseline Reference)</option>
            <option value="Other">Other International Jurisdiction</option>
          </select>
        </div>

        {/* State / UT Searchable Dropdown */}
        <div style={{ position: 'relative' }}>
          <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '5px' }}>
            State / Union Territory
          </label>
          <div
            onClick={() => setShowStateDropdown(!showStateDropdown)}
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
              color: stateUt ? 'var(--text-main)' : 'var(--text-dim)',
              fontSize: '0.84rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {stateUt || 'Select State / UT'}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>▼</span>
          </div>

          {showStateDropdown && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                zIndex: 50,
                marginTop: '4px',
                background: 'var(--bg-card)',
                border: '1px solid var(--accent-cyan-border, rgba(14, 165, 233, 0.4))',
                borderRadius: 'var(--radius-sm)',
                boxShadow: 'var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.5))',
                maxHeight: '260px',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <div style={{ padding: '8px', borderBottom: '1px solid var(--border-subtle)' }}>
                <input
                  type="text"
                  autoFocus
                  placeholder="Search 28 states & 8 UTs..."
                  value={stateSearch}
                  onChange={(e) => setStateSearch(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '4px',
                    padding: '6px 8px',
                    color: 'var(--text-main)',
                    fontSize: '0.8rem'
                  }}
                />
              </div>
              <div style={{ overflowY: 'auto', flex: 1 }}>
                {filteredStates.map((s) => (
                  <div
                    key={s}
                    onClick={() => handleStateSelect(s)}
                    style={{
                      padding: '8px 12px',
                      fontSize: '0.82rem',
                      cursor: 'pointer',
                      color: stateUt === s ? 'var(--accent-cyan)' : 'var(--text-main)',
                      background: stateUt === s ? 'rgba(14, 165, 233, 0.12)' : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                    onMouseEnter={(e) => {
                      if (stateUt !== s) e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                    }}
                    onMouseLeave={(e) => {
                      if (stateUt !== s) e.currentTarget.style.background = 'transparent';
                    }}
                  >
                    <span>{s}</span>
                    {stateUt === s && <Check size={14} />}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* District Searchable Dropdown */}
        <div style={{ position: 'relative' }}>
          <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '5px' }}>
            District (Dependent on State/UT)
          </label>
          <div
            onClick={() => setShowDistrictDropdown(!showDistrictDropdown)}
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
              color: district ? 'var(--text-main)' : 'var(--text-dim)',
              fontSize: '0.84rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {district || 'Select District'}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>▼</span>
          </div>

          {showDistrictDropdown && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                zIndex: 50,
                marginTop: '4px',
                background: 'var(--bg-card)',
                border: '1px solid var(--accent-cyan-border, rgba(14, 165, 233, 0.4))',
                borderRadius: 'var(--radius-sm)',
                boxShadow: 'var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.5))',
                maxHeight: '260px',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <div style={{ padding: '8px', borderBottom: '1px solid var(--border-subtle)' }}>
                <input
                  type="text"
                  autoFocus
                  placeholder={`Search ${stateUt || ''} districts...`}
                  value={districtSearch}
                  onChange={(e) => setDistrictSearch(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '4px',
                    padding: '6px 8px',
                    color: 'var(--text-main)',
                    fontSize: '0.8rem'
                  }}
                />
              </div>
              <div style={{ overflowY: 'auto', flex: 1 }}>
                {filteredDistricts.map((d) => (
                  <div
                    key={d}
                    onClick={() => handleDistrictSelect(d)}
                    style={{
                      padding: '8px 12px',
                      fontSize: '0.82rem',
                      cursor: 'pointer',
                      color: district === d ? 'var(--accent-cyan)' : 'var(--text-main)',
                      background: district === d ? 'rgba(14, 165, 233, 0.12)' : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                    onMouseEnter={(e) => {
                      if (district !== d) e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                    }}
                    onMouseLeave={(e) => {
                      if (district !== d) e.currentTarget.style.background = 'transparent';
                    }}
                  >
                    <span>{d}</span>
                    {district === d && <Check size={14} />}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* City / Town */}
        <div>
          <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '5px' }}>
            City / Town / Taluk
          </label>
          <input
            type="text"
            value={cityTown || ''}
            onChange={(e) => onChange({ city_town: e.target.value })}
            placeholder="e.g. Bengaluru"
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
              color: 'var(--text-main)',
              fontSize: '0.84rem'
            }}
          />
        </div>

        {/* Locality / Police Station */}
        <div>
          <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '5px' }}>
            Locality / Police Station Area
          </label>
          <input
            type="text"
            value={locality || ''}
            onChange={(e) => onChange({ locality: e.target.value })}
            placeholder="e.g. Indiranagar PS"
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
              color: 'var(--text-main)',
              fontSize: '0.84rem'
            }}
          />
        </div>

        {/* PIN Code */}
        <div>
          <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '5px' }}>
            PIN / Postal Code (Optional)
          </label>
          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={pinCode || ''}
            onChange={(e) => handlePinCodeChange(e.target.value)}
            placeholder="e.g. 560038"
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 10px',
              color: 'var(--text-main)',
              fontSize: '0.84rem'
            }}
          />
        </div>
      </div>

      {/* Cross-Geography Educational Disclaimer */}
      <div
        style={{
          marginTop: '14px',
          padding: '10px 14px',
          background: 'rgba(59, 130, 246, 0.08)',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '10px'
        }}
      >
        <Info size={16} style={{ color: '#60a5fa', flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
          <strong style={{ color: '#93c5fd' }}>Cross-Geographic Analytical Context: </strong>
          User-entered Indian location is preserved for investigative tracking.
          The historical reference dataset contains 2,20,663 records from Alabama, USA (2024 FBI NIBRS).
          Behavioral similarity indicates matching operational execution (modus operandi, timing, weapon presence, target selection), not geographic co-location.
        </div>
      </div>
    </div>
  );
};
