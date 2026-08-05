// routes/signup.tsx
import { zodResolver } from "@hookform/resolvers/zod"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

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

const formSchema = z
  .object({
    email: z.string().email({ message: "Invalid email address" }),
    full_name: z.string().min(1, { message: "Full Name is required" }),
    password: z
      .string()
      .min(1, { message: "Password is required" })
      .min(8, { message: "Password must be at least 8 characters" }),
    confirm_password: z
      .string()
      .min(1, { message: "Password confirmation is required" }),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "The passwords don't match",
    path: ["confirm_password"],
  })

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/signup")({
  component: SignUp,
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
        title: "Sign Up - FastAPI Template",
      },
    ],
  }),
})

function SignUp() {
  const { signUpMutation } = useAuth()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  })

  const onSubmit = (data: FormData) => {
    if (signUpMutation.isPending) return

    // exclude confirm_password from submission data
    const { confirm_password: _confirm_password, ...submitData } = data
    signUpMutation.mutate(submitData)
  }

  return (
    <AuthLayout>
      <div>
        {/* Header Section */}
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-300 to-indigo-300 bg-clip-text text-transparent">
            Create an account
          </h1>
          <p className="mt-2 text-sm text-blue-200/70 tracking-wide">
            Join us today and get started!
          </p>
        </div>

        {/* Form Controls Section */}
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="mt-6 space-y-4"
          >
            <FormField
              control={form.control}
              name="full_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="block text-xs font-medium text-white/50 uppercase tracking-wider mb-1">
                    Full Name
                  </FormLabel>
                  <FormControl>
                    <Input
                      data-testid="full-name-input"
                      placeholder="Michael Scott"
                      type="text"
                      className="w-full input-clean rounded-xl px-4 py-2.5 text-sm placeholder:text-sm bg-white/5 border border-white/10 text-white focus:border-blue-400"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs text-red-400 mt-1" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
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
                      className="w-full input-clean rounded-xl px-4 py-2.5 text-sm placeholder:text-sm bg-white/5 border border-white/10 text-white focus:border-blue-400"
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
                      className="w-full input-clean rounded-xl px-4 py-2.5 text-sm placeholder:text-sm bg-white/5 border border-white/10 text-white focus:border-blue-400"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs text-red-400 mt-1" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirm_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="block text-xs font-medium text-white/50 uppercase tracking-wider mb-1">
                    Confirm Password
                  </FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="confirm-password-input"
                      placeholder="••••••••"
                      className="w-full input-clean rounded-xl px-4 py-2.5 text-sm placeholder:text-sm bg-white/5 border border-white/10 text-white focus:border-blue-400"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs text-red-400 mt-1" />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              loading={signUpMutation.isPending}
              className="w-full btn-primary text-white font-semibold py-3.5 rounded-xl text-base shadow-lg shadow-blue-500/20 bg-gradient-to-r from-blue-500 to-indigo-600 hover:opacity-90 transition-opacity mt-2"
            >
              Sign Up
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
                className="social-btn flex items-center justify-center gap-2 rounded-xl py-2 text-xs font-medium border border-white/10 bg-white/5 hover:bg-white/10 transition text-white"
              >
                <i className="fab fa-apple text-base"></i> Sign up with Apple
              </button>
              <button
                type="button"
                className="social-btn flex items-center justify-center gap-2 rounded-xl py-2 text-xs font-medium border border-white/10 bg-white/5 hover:bg-white/10 transition text-white"
              >
                <i className="fab fa-google text-base"></i> Sign up with Google
              </button>
            </div>
          </form>
        </Form>
      </div>

      {/* Footer Section */}
      <div className="mt-6 text-center md:text-left">
        <p className="text-xs text-white/40">
          Already have an account?{" "}
          <RouterLink
            to="/login"
            className="text-blue-300 underline underline-offset-2 hover:text-blue-200"
          >
            Log in
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
// import { zodResolver } from "@hookform/resolvers/zod"
// import {
//   createFileRoute,
//   Link as RouterLink,
//   redirect,
// } from "@tanstack/react-router"
// import { useForm } from "react-hook-form"
// import { z } from "zod"
// import { AuthLayout } from "@/components/Common/AuthLayout"
// import {
//   Form,
//   FormControl,
//   FormField,
//   FormItem,
//   FormLabel,
//   FormMessage,
// } from "@/components/ui/form"
// import { Input } from "@/components/ui/input"
// import { LoadingButton } from "@/components/ui/loading-button"
// import { PasswordInput } from "@/components/ui/password-input"
// import useAuth, { isLoggedIn } from "@/hooks/useAuth"

// const formSchema = z
//   .object({
//     email: z.email({ message: "Invalid email address" }),
//     full_name: z.string().min(1, { message: "Full Name is required" }),
//     password: z
//       .string()
//       .min(1, { message: "Password is required" })
//       .min(8, { message: "Password must be at least 8 characters" }),
//     confirm_password: z
//       .string()
//       .min(1, { message: "Password confirmation is required" }),
//   })
//   .refine((data) => data.password === data.confirm_password, {
//     message: "The passwords don't match",
//     path: ["confirm_password"],
//   })

// type FormData = z.infer<typeof formSchema>

// export const Route = createFileRoute("/signup")({
//   component: SignUp,
//   beforeLoad: async () => {
//     if (isLoggedIn()) {
//       throw redirect({
//         to: "/",
//       })
//     }
//   },
//   head: () => ({
//     meta: [
//       {
//         title: "Sign Up - FastAPI Template",
//       },
//     ],
//   }),
// })

// function SignUp() {
//   const { signUpMutation } = useAuth()
//   const form = useForm<FormData>({
//     resolver: zodResolver(formSchema),
//     mode: "onBlur",
//     criteriaMode: "all",
//     defaultValues: {
//       email: "",
//       full_name: "",
//       password: "",
//       confirm_password: "",
//     },
//   })

//   const onSubmit = (data: FormData) => {
//     if (signUpMutation.isPending) return

//     // exclude confirm_password from submission data
//     const { confirm_password: _confirm_password, ...submitData } = data
//     signUpMutation.mutate(submitData)
//   }

//   return (
//     <AuthLayout>
//       <Form {...form}>
//         <form
//           onSubmit={form.handleSubmit(onSubmit)}
//           className="flex flex-col gap-6"
//         >
//           <div className="flex flex-col items-center gap-2 text-center">
//             <h1 className="text-2xl font-bold">Create an account</h1>
//           </div>

//           <div className="grid gap-4">
//             <FormField
//               control={form.control}
//               name="full_name"
//               render={({ field }) => (
//                 <FormItem>
//                   <FormLabel>Full Name</FormLabel>
//                   <FormControl>
//                     <Input
//                       data-testid="full-name-input"
//                       placeholder="User"
//                       type="text"
//                       {...field}
//                     />
//                   </FormControl>
//                   <FormMessage />
//                 </FormItem>
//               )}
//             />

//             <FormField
//               control={form.control}
//               name="email"
//               render={({ field }) => (
//                 <FormItem>
//                   <FormLabel>Email</FormLabel>
//                   <FormControl>
//                     <Input
//                       data-testid="email-input"
//                       placeholder="user@example.com"
//                       type="email"
//                       {...field}
//                     />
//                   </FormControl>
//                   <FormMessage />
//                 </FormItem>
//               )}
//             />

//             <FormField
//               control={form.control}
//               name="password"
//               render={({ field }) => (
//                 <FormItem>
//                   <FormLabel>Password</FormLabel>
//                   <FormControl>
//                     <PasswordInput
//                       data-testid="password-input"
//                       placeholder="Password"
//                       {...field}
//                     />
//                   </FormControl>
//                   <FormMessage />
//                 </FormItem>
//               )}
//             />

//             <FormField
//               control={form.control}
//               name="confirm_password"
//               render={({ field }) => (
//                 <FormItem>
//                   <FormLabel>Confirm Password</FormLabel>
//                   <FormControl>
//                     <PasswordInput
//                       data-testid="confirm-password-input"
//                       placeholder="Confirm Password"
//                       {...field}
//                     />
//                   </FormControl>
//                   <FormMessage />
//                 </FormItem>
//               )}
//             />

//             <LoadingButton
//               type="submit"
//               className="w-full"
//               loading={signUpMutation.isPending}
//             >
//               Sign Up
//             </LoadingButton>
//           </div>

//           <div className="text-center text-sm">
//             Already have an account?{" "}
//             <RouterLink to="/login" className="underline underline-offset-4">
//               Log in
//             </RouterLink>
//           </div>
//         </form>
//       </Form>
//     </AuthLayout>
//   )
// }
