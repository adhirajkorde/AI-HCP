import React from 'react';

export const CardSkeleton = () => (
  <div className="card skeleton-card" style={{ pointerEvents: 'none' }}>
    <div className="skeleton skeleton-title" />
    <div className="skeleton skeleton-line" />
    <div className="skeleton skeleton-line" style={{ width: '80%' }} />
    <div className="skeleton skeleton-line" style={{ width: '60%' }} />
    <style>{`
      .skeleton-card {
        display: flex;
        flex-direction: column;
        gap: 12px;
        min-height: 180px;
      }
      .skeleton-title {
        height: 24px;
        width: 40%;
        margin-bottom: 8px;
      }
      .skeleton-line {
        height: 16px;
        width: 100%;
      }
    `}</style>
  </div>
);

export const TableSkeleton = ({ rows = 4 }) => (
  <div className="card" style={{ pointerEvents: 'none', padding: '1.5rem' }}>
    <div className="skeleton" style={{ height: '32px', width: '30%', marginBottom: '1.5rem' }} />
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ display: 'flex', gap: '20px' }}>
          <div className="skeleton" style={{ height: '20px', flex: 1 }} />
          <div className="skeleton" style={{ height: '20px', flex: 2 }} />
          <div className="skeleton" style={{ height: '20px', flex: 1 }} />
          <div className="skeleton" style={{ height: '20px', width: '80px' }} />
        </div>
      ))}
    </div>
  </div>
);

export const StatsSkeleton = () => (
  <div className="stats-skeleton-grid">
    {Array.from({ length: 4 }).map((_, i) => (
      <div key={i} className="card skeleton-stat-card" style={{ pointerEvents: 'none' }}>
        <div className="skeleton" style={{ height: '14px', width: '50%' }} />
        <div className="skeleton" style={{ height: '36px', width: '35%', marginTop: '12px' }} />
        <div className="skeleton" style={{ height: '12px', width: '70%', marginTop: '8px' }} />
      </div>
    ))}
    <style>{`
      .stats-skeleton-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
      }
      .skeleton-stat-card {
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
    `}</style>
  </div>
);
