/**
 * Auth Debug Page - Temporary debugging page
 */

import React, { useEffect, useState } from 'react';
import Card from '../components/ui/Card';
import { Button } from '../components/ui/shadcn/button';

const AuthDebugPage: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [decoded, setDecoded] = useState<any>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    setToken(storedToken);

    if (storedToken) {
      try {
        const parts = storedToken.split('.');
        if (parts.length === 3) {
          const payload = JSON.parse(atob(parts[1]));
          setDecoded(payload);
        }
      } catch (e) {
        console.error('Failed to decode token:', e);
      }
    }
  }, []);

  const testGovernanceAPI = async () => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('http://localhost:8000/api/v1/change-log', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    console.log('Response status:', response.status);
    const data = await response.json();
    console.log('Response data:', data);
    alert(`Status: ${response.status}\nData: ${JSON.stringify(data, null, 2)}`);
  };

  return (
    <div className="min-h-screen bg-bg-base p-8">
      <Card padding="lg">
        <h1 className="text-2xl font-bold mb-4">Auth Debug</h1>

        <div className="space-y-4">
          <div>
            <h2 className="font-semibold mb-2">Token Status:</h2>
            <p className="text-sm">{token ? 'Token found' : 'No token in localStorage'}</p>
          </div>

          {token && (
            <>
              <div>
                <h2 className="font-semibold mb-2">Token:</h2>
                <pre className="text-xs bg-white/5 p-2 rounded overflow-x-auto">
                  {token}
                </pre>
              </div>

              {decoded && (
                <div>
                  <h2 className="font-semibold mb-2">Decoded Payload:</h2>
                  <pre className="text-xs bg-white/5 p-2 rounded">
                    {JSON.stringify(decoded, null, 2)}
                  </pre>
                  <p className="text-sm mt-2">
                    Expires: {new Date(decoded.exp * 1000).toLocaleString()}
                    {decoded.exp * 1000 < Date.now() && (
                      <span className="text-error ml-2">(EXPIRED!)</span>
                    )}
                  </p>
                </div>
              )}

              <div>
                <Button onClick={testGovernanceAPI}>
                  Test Governance API
                </Button>
              </div>
            </>
          )}

          {!token && (
            <div className="text-warning">
              Please log in first to get an auth token
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default AuthDebugPage;
