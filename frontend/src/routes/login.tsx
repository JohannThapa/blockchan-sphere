import { zodResolver } from "@hookform/resolvers/zod"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import type { Body_login_login_access_token as AccessToken } from "@/client"
import { AuthLayout } from "@/components/Common/AuthLayout"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"

const formSchema = z.object({
  username: z.string().email({ message: "Invalid email address" }),
  password: z
    .string()
    .min(1, { message: "Password is required" })
    .min(8, { message: "Password must be at least 8 characters" }),
}) satisfies z.ZodType<AccessToken>

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Log In - FastAPI Template",
      },
    ],
  }),
})

function Login() {
  const { loginMutation } = useAuth()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit = (data: FormData) => {
    if (loginMutation.isPending) return
    loginMutation.mutate(data)
  }

  return (
    <AuthLayout>
      <div>
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight bg-linear-to-r from-blue-300 to-indigo-300 bg-clip-text text-transparent">
            Login to your account
          </h1>
          <p className="mt-2 text-sm text-blue-200/70 tracking-wide">
            Welcome Back!
          </p>
        </div>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="mt-6 space-y-5"
          >
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="block text-xs font-medium text-white/50 uppercase tracking-wider mb-1">
                    Email
                  </FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder="michael@example.com"
                      type="email"
                      className="w-full input-clean rounded-xl px-4 py-3 text-sm placeholder:text-sm bg-white/5 border border-white/10 text-white focus:border-blue-400"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs text-red-400 mt-1" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="block text-xs font-medium text-white/50 uppercase tracking-wider mb-1">
                    Password
                  </FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="••••••••"
                      className="w-full input-clean rounded-xl px-4 py-3 text-sm placeholder:text-sm bg-white/5 border border-white/10 text-white focus:border-blue-400"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs text-red-400 mt-1" />
                </FormItem>
              )}
            />

            <div className="flex justify-between items-center text-sm">
              <label className="flex items-center gap-2 text-white/70 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="check-custom rounded accent-blue-500"
                />
                <span className="text-xs">Remember me</span>
              </label>
              <RouterLink
                to="/recover-password"
                className="text-blue-300/80 hover:text-blue-200 transition text-xs font-medium"
              >
                Forgot Password?
              </RouterLink>
            </div>

            <LoadingButton
              type="submit"
              loading={loginMutation.isPending}
              className="w-full btn-primary text-white font-semibold py-3.5 rounded-xl text-base shadow-lg shadow-blue-500/20 bg-gradient-to-r from-blue-500 to-indigo-600 hover:opacity-90 transition-opacity"
            >
              Login
            </LoadingButton>

            <div className="flex items-center gap-3 my-2">
              <hr className="flex-1 border-white/10" />
              <span className="text-white/30 text-xs font-light tracking-wider">
                OR
              </span>
              <hr className="flex-1 border-white/10" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                className="social-btn flex items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-medium border border-white/10 bg-white/5 hover:bg-white/10 transition"
              >
                <i className="fab fa-apple text-base"></i> Log in with Apple
              </button>
              <button
                type="button"
                className="social-btn flex items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-medium border border-white/10 bg-white/5 hover:bg-white/10 transition"
              >
                <i className="fab fa-google text-base"></i> Log in with Google
              </button>
            </div>
          </form>
        </Form>
      </div>

      <div className="mt-8 text-center md:text-left">
        <p className="text-xs text-white/40">
          Don't have an account yet?{" "}
          <RouterLink
            to="/signup"
            className="text-blue-300 underline underline-offset-2 hover:text-blue-200"
          >
            Sign up
          </RouterLink>
        </p>
        <p className="text-[0.6rem] mt-2 text-white/30">
          © 2026 Johann. All rights reserved. Unauthorized use or reproduction of
          any content or materials from this site is prohibited. For more
          information, visit our{" "}
          <a
            href="#"
            className="text-white/50 hover:text-white/70 underline underline-offset-2"
          >
            Terms of Service
          </a>{" "}
          and{" "}
          <a
            href="#"
            className="text-white/50 hover:text-white/70 underline underline-offset-2"
          >
            Privacy Policy
          </a>
          .
        </p>
      </div>
    </AuthLayout>
  )
}