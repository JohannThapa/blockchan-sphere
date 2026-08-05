import { Appearance } from "@/components/Common/Appearance"
// import { Logo } from "@/components/Common/Logo"
import { Footer } from "./Footer"
import WaveContainer from "../ui/containers/wave-container";

interface AuthLayoutProps {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div>
    <div className="min-h-screen relative w-full flex items-center justify-center bg-[#010514] font-sans p-4">
    <div className="w-full max-w-5xl login-card overflow-hidden bg-[#101d34] flex flex-col md:flex-row shadow-2xl rounded-3xl">
 
      <div className="w-full md:w-1/2 p-8 md:p-10 lg:p-12 flex flex-col justify-between bg-[#111b2e] text-white">
        {children}
      </div>
       <div className="absolute top-4 right-4">
       <Appearance />
      </div>
      <WaveContainer />
    </div>
  </div>
  <Footer />
  </div>
    // <div className="grid min-h-svh lg:grid-cols-2">
    //   <div className="bg-muted dark:bg-zinc-900 relative hidden lg:flex lg:items-center lg:justify-center">
    //     <Logo variant="full" className="h-16" asLink={false} />
    //   </div>
    //   <div className="flex flex-col gap-4 p-6 md:p-10">
    //     <div className="flex justify-end">
    //       <Appearance />
    //     </div>
    //     <div className="flex flex-1 items-center justify-center">
    //       <div className="w-full max-w-xs">{children}</div>
    //     </div>
    //     <Footer />
    //   </div>
    // </div>
  )
}
