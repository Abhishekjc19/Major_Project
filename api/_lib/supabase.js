const getSupabaseConfig = () => {
  const url = process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !serviceKey) {
    throw new Error('Server is missing Supabase environment variables');
  }

  return {
    baseUrl: `${url.replace(/\/$/, '')}/rest/v1`,
    serviceKey,
  };
};

async function supabaseRequest(path, options = {}) {
  const { baseUrl, serviceKey } = getSupabaseConfig();
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message = data?.message || data?.details || 'Database request failed';
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return data;
}

export async function findUserByEmail(email) {
  const encodedEmail = encodeURIComponent(email);
  const users = await supabaseRequest(
    `/users?email=eq.${encodedEmail}&select=*`,
  );

  return users[0] || null;
}

export async function findUserById(id) {
  const encodedId = encodeURIComponent(id);
  const users = await supabaseRequest(`/users?id=eq.${encodedId}&select=*`);

  return users[0] || null;
}

export async function createUser(user) {
  const users = await supabaseRequest('/users?select=*', {
    method: 'POST',
    headers: {
      Prefer: 'return=representation',
    },
    body: JSON.stringify(user),
  });

  return users[0];
}

export async function listBuses() {
  return supabaseRequest('/buses?select=*&order=route_number.asc');
}
