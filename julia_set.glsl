void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec2 uv = fragCoord/iResolution.xy;
    vec3 col = vec3(0.);
    float t = pow(2., iTime);

    int n = 0;
    float a = (uv.x-0.5)*2.5/t-.745;
    float b = (uv.y-0.5)*2./t+.186;
    int max_iter = 100;
    float fmax_iter = float(max_iter);
    while (n < max_iter) {
        float aa = a*a - b*b;
        float bb = 2. * a * b;
        a = aa + (iMouse.y*2.)/iResolution.y-1.;
        b = bb + (iMouse.x*2.)/iResolution.x-1.;
        
        if (abs(a+b) > 16.) {
            break;
        }
        n++;
    }
    if (n == max_iter) {
        col = vec3(1.);
    } else { // Stolen from shadertoy
        float sl = float(n) - log2(log2(a*a+b*b)) + 4.0;

        float al = smoothstep( -0.1, 0.0, sin(0.5*6.2831*iTime ) );
        float l = mix( float(n), sl, al );
        col += 0.5 + 0.5*cos( 3.0 + l*0.15 + vec3(0.0,0.6,1.0));
    }

    fragColor = vec4(col,1.0);
}