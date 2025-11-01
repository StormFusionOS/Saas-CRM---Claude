import React from 'react';

const DashboardPage: React.FC = () => {
  return (
    <div className="p-8 bg-gray-900 min-h-screen text-white">
      <h1 className="text-3xl font-bold mb-6">Ops Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Services</h3>
          <p className="text-3xl font-bold text-green-500">12 / 12</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Alerts</h3>
          <p className="text-3xl font-bold text-yellow-500">3</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">CPU Usage</h3>
          <p className="text-3xl font-bold text-blue-500">45%</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
