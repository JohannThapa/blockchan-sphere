import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import logo from "/assets/transparent-logo.png";
import { cn } from '@/lib/utils';
interface WaveUniforms {
  uTime: { value: number };
  uHue: { value: number };
  uHueVariation: { value: number };
  uGradient: { value: number };
  uDensity: { value: number };
  uDisplacement: { value: number };
  uMousePosition: { value: THREE.Vector2 };
}

const WaveContainer: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.OrthographicCamera | null>(null);
  const planeRef = useRef<THREE.Mesh<THREE.PlaneGeometry, THREE.ShaderMaterial> | null>(null);
  const mousePosRef = useRef<{ x: number; y: number }>({ x: 0.5, y: 0.5 });
  const targetMousePosRef = useRef<{ x: number; y: number }>({ x: 0.5, y: 0.5 });
  const timerRef = useRef<number>(0);
  const animationFrameRef = useRef<number | null>(null);

  const vertexShader = `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = vec4(position, 1.0);
    }
  `;

  const fragmentShader = `
    precision highp float;

    uniform float uTime;
    uniform vec2 uMousePosition;
    uniform float uHue;
    uniform float uHueVariation;
    uniform float uDensity;
    uniform float uDisplacement;
    uniform float uGradient;
    
    varying vec2 vUv;

    float mod289(float x){return x - floor(x * (1.0 / 289.0)) * 289.0;}
    vec4 mod289(vec4 x){return x - floor(x * (1.0 / 289.0)) * 289.0;}
    vec4 perm(vec4 x){return mod289(((x * 34.0) + 1.0) * x);}

    float rand(vec2 co){
      return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
    }

    float hue2rgb(float f1, float f2, float hue) {
        if (hue < 0.0)
            hue += 1.0;
        else if (hue > 1.0)
            hue -= 1.0;
        float res;
        if ((6.0 * hue) < 1.0)
            res = f1 + (f2 - f1) * 6.0 * hue;
        else if ((2.0 * hue) < 1.0)
            res = f2;
        else if ((3.0 * hue) < 2.0)
            res = f1 + (f2 - f1) * ((2.0 / 3.0) - hue) * 6.0;
        else
            res = f1;
        return res;
    }

    vec3 hsl2rgb(vec3 hsl) {
        vec3 rgb;
        if (hsl.y == 0.0) {
            rgb = vec3(hsl.z);
        } else {
            float f2;
            if (hsl.z < 0.5)
                f2 = hsl.z * (1.0 + hsl.y);
            else
                f2 = hsl.z + hsl.y - hsl.y * hsl.z;
            float f1 = 2.0 * hsl.z - f2;
            rgb.r = hue2rgb(f1, f2, hsl.x + (1.0/3.0));
            rgb.g = hue2rgb(f1, f2, hsl.x);
            rgb.b = hue2rgb(f1, f2, hsl.x - (1.0/3.0));
        }
        return rgb;
    }

    vec3 hsl2rgb(float h, float s, float l) {
        return hsl2rgb(vec3(h, s, l));
    }

    float noise(vec3 p){
        vec3 a = floor(p);
        vec3 d = p - a;
        d = d * d * (3.0 - 2.0 * d);
        vec4 b = a.xxyy + vec4(0.0, 1.0, 0.0, 1.0);
        vec4 k1 = perm(b.xyxy);
        vec4 k2 = perm(k1.xyxy + b.zzww);
        vec4 c = k2 + a.zzzz;
        vec4 k3 = perm(c);
        vec4 k4 = perm(c + 1.0);
        vec4 o1 = fract(k3 * (1.0 / 41.0));
        vec4 o2 = fract(k4 * (1.0 / 41.0));
        vec4 o3 = o2 * d.z + o1 * (1.0 - d.z);
        vec2 o4 = o3.yw * d.x + o3.xz * (1.0 - d.x);
        return o4.y * d.y + o4.x * (1.0 - d.y);
    }

    vec2 fade(vec2 t) {return t*t*t*(t*(t*6.0-15.0)+10.0);}

    float cnoise(vec2 P){
        vec4 Pi = floor(P.xyxy) + vec4(0.0, 0.0, 1.0, 1.0);
        vec4 Pf = fract(P.xyxy) - vec4(0.0, 0.0, 1.0, 1.0);
        Pi = mod(Pi, 289.0);
        vec4 ix = Pi.xzxz;
        vec4 iy = Pi.yyww;
        vec4 fx = Pf.xzxz;
        vec4 fy = Pf.yyww;
        vec4 i = perm(perm(ix) + iy);
        vec4 gx = 2.0 * fract(i * 0.0243902439) - 1.0;
        vec4 gy = abs(gx) - 0.5;
        vec4 tx = floor(gx + 0.5);
        gx = gx - tx;
        vec2 g00 = vec2(gx.x,gy.x);
        vec2 g10 = vec2(gx.y,gy.y);
        vec2 g01 = vec2(gx.z,gy.z);
        vec2 g11 = vec2(gx.w,gy.w);
        vec4 norm = 1.79284291400159 - 0.85373472095314 *
        vec4(dot(g00, g00), dot(g01, g01), dot(g10, g10), dot(g11, g11));
        g00 *= norm.x;
        g01 *= norm.y;
        g10 *= norm.z;
        g11 *= norm.w;
        float n00 = dot(g00, vec2(fx.x, fy.x));
        float n10 = dot(g10, vec2(fx.y, fy.y));
        float n01 = dot(g01, vec2(fx.z, fy.z));
        float n11 = dot(g11, vec2(fx.w, fy.w));
        vec2 fade_xy = fade(Pf.xy);
        vec2 n_x = mix(vec2(n00, n01), vec2(n10, n11), fade_xy.x);
        float n_xy = mix(n_x.x, n_x.y, fade_xy.y);
        return 2.3 * n_xy;
    }

    void main () {
      float mouseDistance = length(vUv - uMousePosition);
      float t = uTime * .005;
      float elevation =  vUv.y * uDensity * 30.0;
      
      float shadow = smoothstep(0.0, .3 + sin(t * 5.0 * 3.14) * .1 , mouseDistance);
      elevation += shadow * 5.0;
      
      float displacement = cnoise( vec2( t + vUv.y * 2.0, t + vUv.x * 3.0 )) * uDisplacement * 3.0 ;
      elevation += displacement * 4.0;
      elevation *= 2.0 + cnoise( vec2( t + vUv.y * 1.0, t + .5)) * 2.0 ;
      
      float light = .9 + fract(elevation) ;
      light *= .9 + (1.0 - (displacement * displacement)) * .1;
      elevation = floor(elevation);
    
      float hue =  uHue + shadow * .1 + cnoise( vec2( elevation * .10, .1 + t)) * uHueVariation;
      float saturation = .6;
      float brightness =  - (1.0 - shadow) * .1 + .5  - smoothstep( 0.0, .9,  cnoise( vec2( elevation * .5, .4 + t * 5.0)) ) * .1;

      vec3 hslCol = vec3( hue, saturation, brightness);
      vec3 col = hsl2rgb(hslCol) * vec3(light, 1.0, 1.0);
      
      gl_FragColor = vec4(col, 1.);
    }
  `;

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);
    renderer.setClearColor(0x111b2e, 1);

    renderer.domElement.style.position = 'absolute';
    renderer.domElement.style.top = '0';
    renderer.domElement.style.left = '0';
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';

    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    cameraRef.current = camera;

    const uniforms: WaveUniforms = {
      uTime: { value: 0 },
      uHue: { value: 0.5 },
      uHueVariation: { value: 1.0 },
      uGradient: { value: 1.0 },
      uDensity: { value: 0.5 },
      uDisplacement: { value: 0.66 },
      uMousePosition: { value: new THREE.Vector2(0.5, 0.5) },
    };

    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: uniforms as any,
    });

    const geometry = new THREE.PlaneGeometry(2, 2);
    const plane = new THREE.Mesh(geometry, material);
    scene.add(plane);
    planeRef.current = plane;

    const speed = 0.2;
    const animate = () => {
      timerRef.current += speed;
      if (planeRef.current) {
        const mat = planeRef.current.material as THREE.ShaderMaterial;
        mat.uniforms.uTime.value = timerRef.current;

        mousePosRef.current.x += (targetMousePosRef.current.x - mousePosRef.current.x) * 0.1;
        mousePosRef.current.y += (targetMousePosRef.current.y - mousePosRef.current.y) * 0.1;

        (mat.uniforms.uMousePosition.value as THREE.Vector2).set(
          mousePosRef.current.x,
          mousePosRef.current.y
        );
      }

      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      if (!container || !rendererRef.current) return;
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      rendererRef.current.setSize(newWidth, newHeight);
    };

    window.addEventListener('resize', handleResize);

    const handleMouseMove = (e: MouseEvent) => {
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = 1.0 - (e.clientY - rect.top) / rect.height;
      targetMousePosRef.current = { x, y };
    };

    document.addEventListener('mousemove', handleMouseMove);

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (rendererRef.current) {
        rendererRef.current.dispose();
      }
      if (planeRef.current) {
        planeRef.current.geometry.dispose();
        planeRef.current.material.dispose();
      }
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('mousemove', handleMouseMove);
      if (container && rendererRef.current && rendererRef.current.domElement) {
        container.removeChild(rendererRef.current.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full md:w-1/2 min-h-80 md:min-h-150 relative overflow-hidden rounded-b-2xl md:rounded-r-2xl md:rounded-l-none"
      style={{ background: '#111b2e' }}
    >
      {/* Overlay Content */}
      <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
        <div className="text-center px-6">

        <img
          src={logo}
          alt="FastAPI"
          className={cn(
            "h-auto md:h-auto w-96 md:w-lg mx-auto",
            '',
          )}
        />
          {/* <p className="text-blue-200/50 text-sm md:text-base mt-2 font-dark tracking-wide">
          Blockchain Intelligence & Digital Asset Infrastructure Platform
          </p> */}
          {/* <div className="mt-4 flex justify-center gap-2 text-white/20 text-xs">
            <span className="w-2 h-2 rounded-full bg-blue-400/40"></span>
            <span className="w-2 h-2 rounded-full bg-indigo-400/40"></span>
            <span className="w-2 h-2 rounded-full bg-blue-300/40"></span>
          </div> */}
        </div>
      </div>
    </div>
  );
};

export default WaveContainer;