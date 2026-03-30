"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/sidebar";

const CONTACT_RECEIVER_EMAIL = "manavbagthaliya.ai@gmail.com";

export default function ContactUs() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  React.useEffect(() => {
    if (!submitStatus) {
      return;
    }

    const timer = setTimeout(() => {
      setSubmitStatus(null);
    }, 5000);

    return () => clearTimeout(timer);
  }, [submitStatus]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const response = await fetch(
        `https://formsubmit.co/ajax/${CONTACT_RECEIVER_EMAIL}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            message: formData.message,
            _subject: "New Contact Form Message - PhysioVision",
            _template: "table",
            _captcha: "false",
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Unable to send message.");
      }

      setFormData({ name: "", email: "", message: "" });
      setSubmitStatus({
        type: "success",
        message: "Message sent successfully.",
      });
    } catch (error) {
      console.error("Email send error:", error);
      setSubmitStatus({
        type: "error",
        message: "Failed to send message. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-gray-200 flex overflow-hidden">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      <div
        className={`flex-grow transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        <div className="flex flex-col items-center justify-center min-h-screen w-full px-8">
          <div className="w-full max-w-lg bg-slate-900 p-6 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300">
            <div className="text-center text-3xl font-semibold text-gray-100 tracking-wide mb-4">
              Contact Us
            </div>
            <div className="text-center text-md font-medium text-gray-400 mb-6">
              <p>
                We'd love to hear from you! Please fill out the form below. 🚀
              </p>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <input
                name="name"
                type="text"
                placeholder="Enter your name"
                className="w-full p-3 text-white bg-slate-950 rounded-md focus:outline-none focus:ring-2 focus:ring-[#7a73c1]"
                value={formData.name}
                onChange={handleChange}
                required
              />
              <input
                name="email"
                type="email"
                placeholder="Enter your email"
                className="w-full p-3 text-white bg-slate-950 rounded-md focus:outline-none focus:ring-2 focus:ring-[#7a73c1]"
                value={formData.email}
                onChange={handleChange}
                required
              />
              <textarea
                name="message"
                rows={4}
                placeholder="Write your message here..."
                className="w-full p-3 text-white bg-slate-950 rounded-md focus:outline-none focus:ring-2 focus:ring-[#7a73c1]"
                value={formData.message}
                onChange={handleChange}
                required
              />
              <div className="flex justify-center">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-3 text-white bg-[#42499b] rounded-md hover:bg-[#7a73c1] transition-all text-sm font-semibold"
                >
                  {isSubmitting ? "Sending..." : "Submit"}
                </button>
              </div>
              {submitStatus ? (
                <p
                  className={`text-center text-sm ${
                    submitStatus.type === "success"
                      ? "text-emerald-400"
                      : "text-red-400"
                  }`}
                >
                  {submitStatus.message}
                </p>
              ) : null}
            </form>

            <div className="text-center text-gray-500 text-sm mt-6">
              <p>
                We respect your privacy and will never share your information.
                💜
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
