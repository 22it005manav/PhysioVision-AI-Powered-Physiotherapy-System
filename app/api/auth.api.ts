import { POST } from "@/utils/api.service";

interface AuthUser {
  username: string;
}

interface LoginResponse {
  success: boolean;
  user: AuthUser;
  message?: string;
}

interface RegisterResponse {
  success?: boolean;
  message: string;
  user?: AuthUser;
}

export const login = async ({
  username,
  password,
}: {
  username: string;
  password: string;
}): Promise<AuthUser> => {
  const payload = {
    username: username.trim(),
    password,
  };

  const response = await POST<LoginResponse, { username: string; password: string }>(
    "/api/signin",
    payload
  );

  if (!response?.success || !response?.user?.username) {
    throw new Error("Invalid login response from server.");
  }

  return response.user;
};

export const register = async ({
  name,
  username,
  email,
  password,
}: {
  name: string;
  username: string;
  email: string;
  password: string;
}): Promise<RegisterResponse> => {
  const payload = {
    name: name.trim(),
    username: username.trim(),
    email: email.trim().toLowerCase(),
    password,
  };

  return POST<
    RegisterResponse,
    { name: string; username: string; email: string; password: string }
  >("/api/signup", payload);
};
