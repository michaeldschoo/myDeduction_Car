import React, { useState, useEffect } from 'react';
import { X, Check, Star, Navigation, Calendar, RotateCcw } from 'lucide-react';
import { TripRecord } from '../data/initialTrips';
import { FAVOURITE_PRESETS, FavouritePreset } from '../data/favoritePresets';

interface TripEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (trip: TripRecord) => void;
  tripToEdit?: TripRecord | null;
}

export const TripEditorModal: React.FC<TripEditorModalProps> = ({
  isOpen,
  onClose,
  onSave,
  tripToEdit,
}) => {
  const [date, setDate] = useState('20/09/2026');
  const [startLocation, setStartLocation] = useState('Edu-Kingdom College, High Street, Penrith NSW, Australia');
  const [endLocation, setEndLocation] = useState('Edu-Kingdom College, Sorrell Street, Parramatta NSW, Australia');
  const [tripDetails, setTripDetails] = useState('Regular Visit to HQ');
  const [tripDistance, setTripDistance] = useState(38.61);
  const [returnJourney, setReturnJourney] = useState(true);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('');

  useEffect(() => {
    if (tripToEdit) {
      setDate(tripToEdit.date);
      setStartLocation(tripToEdit.startLocation);
      setEndLocation(tripToEdit.endLocation);
      setTripDetails(tripToEdit.tripDetails);
      setTripDistance(tripToEdit.tripDistance);
      setReturnJourney(tripToEdit.returnJourney);
      setSelectedPresetId('');
    } else {
      // Default to today in DD/MM/YYYY
      const now = new Date();
      const dd = String(now.getDate()).padStart(2, '0');
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const yyyy = now.getFullYear();
      setDate(`${dd}/${mm}/${yyyy}`);
      setSelectedPresetId(FAVOURITE_PRESETS[0].id);
      applyPreset(FAVOURITE_PRESETS[0]);
    }
  }, [tripToEdit, isOpen]);

  const applyPreset = (preset: FavouritePreset) => {
    setStartLocation(preset.startLocation);
    setEndLocation(preset.endLocation);
    setTripDetails(preset.tripDetails);
    setTripDistance(preset.tripDistance);
    setReturnJourney(preset.returnJourney);
  };

  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const presetId = e.target.value;
    setSelectedPresetId(presetId);
    const found = FAVOURITE_PRESETS.find((p) => p.id === presetId);
    if (found) {
      applyPreset(found);
    }
  };

  if (!isOpen) return null;

  const totalKm = returnJourney ? Number((tripDistance * 2).toFixed(2)) : Number(tripDistance.toFixed(2));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newOrUpdatedTrip: TripRecord = {
      id: tripToEdit ? tripToEdit.id : `trip-${Date.now()}`,
      date,
      startLocation,
      endLocation,
      tripDetails,
      tripDistance,
      returnJourney,
      totalKm,
      startOdometer: tripToEdit?.startOdometer,
      endOdometer: tripToEdit?.endOdometer,
    };
    onSave(newOrUpdatedTrip);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200 my-8">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700">
              <Navigation className="w-4 h-4" />
            </span>
            <h3 className="text-base font-bold text-slate-900">
              {tripToEdit ? '운행일지 수정 (Edit Trip)' : '새 운행일지 추가 (Add Trip)'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-200/60 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Quick Preset Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1.5">
              <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
              즐겨찾기 코스로 1초 자동 완성 (Choose from Favourites)
            </label>
            <select
              value={selectedPresetId}
              onChange={handlePresetChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">-- 직접 입력 또는 즐겨찾기 선택 --</option>
              <optgroup label="🔄 왕복 코스 (Round Trips)">
                {FAVOURITE_PRESETS.filter((p) => p.category === 'round').map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.totalKm} km)
                  </option>
                ))}
              </optgroup>
              <optgroup label="➡️ 순환 편도 코스 (One-way Legs)">
                {FAVOURITE_PRESETS.filter((p) => p.category === 'leg').map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.tripDistance} km)
                  </option>
                ))}
              </optgroup>
            </select>
          </div>

          {/* Date */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" /> 운행 날짜 (DD/MM/YYYY)
            </label>
            <input
              type="text"
              required
              placeholder="DD/MM/YYYY (예: 20/09/2026)"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Start Location */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              출발지 (Start Location)
            </label>
            <input
              type="text"
              required
              value={startLocation}
              onChange={(e) => setStartLocation(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* End Location */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              도착지 (End Location)
            </label>
            <input
              type="text"
              required
              value={endLocation}
              onChange={(e) => setEndLocation(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Purpose / Details */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              업무 목적 / 상세 내용 (Trip details)
            </label>
            <input
              type="text"
              required
              value={tripDetails}
              onChange={(e) => setTripDetails(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Distance & Return Trip Toggle */}
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                편도 거리 (km)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.1"
                required
                value={tripDistance}
                onChange={(e) => setTripDistance(parseFloat(e.target.value) || 0)}
                className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                왕복 여부 (Return Trip)
              </label>
              <button
                type="button"
                onClick={() => setReturnJourney(!returnJourney)}
                className={`w-full py-2 px-3 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-1.5 ${
                  returnJourney
                    ? 'bg-amber-50 text-amber-800 border-amber-300'
                    : 'bg-slate-100 text-slate-700 border-slate-200'
                }`}
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{returnJourney ? '왕복 (Yes - 2배 계산)' : '편도 (No)'}</span>
              </button>
            </div>
          </div>

          {/* Computed Total Km preview */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
            <span className="text-xs text-slate-600 font-medium">최종 반영 운행거리 (Total Km)</span>
            <span className="text-base font-black text-indigo-700">{totalKm.toFixed(2)} km</span>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 px-4 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
            >
              취소
            </button>
            <button
              type="submit"
              className="flex-1 py-2.5 px-4 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md transition flex items-center justify-center gap-1.5"
            >
              <Check className="w-4 h-4" />
              <span>{tripToEdit ? '수정 내용 저장' : '운행일지에 추가'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
