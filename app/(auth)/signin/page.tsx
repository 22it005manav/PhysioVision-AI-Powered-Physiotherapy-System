"use client";

import { useState } from "react";
import Link from "next/link";
import { login } from "@/app/api/auth.api";
import { getApiErrorMessage } from "@/utils/apiError";
import { useRouter } from "next/navigation";
import { useUser } from "@/contexts/AppContext";

export default function SignIn() {
  const [username, setUsernameInput] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const router = useRouter();
  const { setUsername } = useUser();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const cleanedUsername = username.trim();
    if (!cleanedUsername || !password) {
      setError("Username and password are required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await login({
        username: cleanedUsername,
        password,
      });
      setUsername(user.username);
      if (typeof window !== "undefined") {
        localStorage.setItem("username", user.username);
      }
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(
        getApiErrorMessage(
          err,
          "Sign in failed. Please check your credentials."
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUsername = e.target.value;
    setUsernameInput(newUsername);
  };

  return (
    <section>
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="py-12 md:py-20">
          <div className="pb-12 text-center">
            <h1 className="text-3xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-gray-200 via-indigo-200 to-gray-50 md:text-4xl">
              Welcome back
            </h1>
          </div>
          <form className="mx-auto max-w-[400px]" onSubmit={handleSignIn}>
            <div className="space-y-5">
              <div>
                <label
                  className="mb-1 block text-sm font-medium text-indigo-200/65"
                  htmlFor="username"
                >
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  className="form-input w-full"
                  placeholder="Your username"
                  required
                  value={username}
                  onChange={handleUsernameChange}
                />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between gap-3">
                  <label
                    className="block text-sm font-medium text-indigo-200/65"
                    htmlFor="password"
                  >
                    Password
                  </label>
                  <Link
                    className="text-sm text-white hover:underline"
                    href="/reset-password"
                  >
                    Forgot?
                  </Link>
                </div>
                <input
                  id="password"
                  type="password"
                  className="form-input w-full"
                  placeholder="Your password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            <div className="mt-6 space-y-5">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn w-full bg-gradient-to-t from-slate-800 to-indigo-500 text-white"
              >
                {isSubmitting ? "Signing in..." : "Sign In"}
              </button>
            </div>
          </form>
          {error ? <p className="text-red-400 text-center mt-4">{error}</p> : null}
        </div>
      </div>
    </section>
  );
}
