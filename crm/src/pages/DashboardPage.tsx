import React from 'react';

const DashboardPage: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">New Leads</h3>
          <p className="text-3xl font-bold text-blue-600">24</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">In Progress</h3>
          <p className="text-3xl font-bold text-yellow-600">12</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Closed Won</h3>
          <p className="text-3xl font-bold text-green-600">8</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
