void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec2 uv = fragCoord/iResolution.xy;
    vec3 col = vec3(0.);
    float t = pow(2., iTime);

    int n = 0;
    float a = (uv.x-0.5)*2.5/t-.745;
    float b = (uv.y-0.5)*2./t+.186;
    float ca = a;
    float cb = b;
    int max_iter = 512*int(pow(iTime, 3.));
    float fmax_iter = float(max_iter);
    while (n < max_iter) {
        // (a+bi)*(a+bi)
        // <=> a*a+a*bi + bi*a+bi*bi;
        // <=> (a²-b²)+2abi;
        
        float aa = a*a - b*b;
        float bb = 2. * a * b;
        a = aa+ca;
        b = bb+cb;
        
        if (abs(a+b) > 256.) {
            break;
        }
        n++;
    }
    if (n == max_iter) {
        col.r = 1.0;
        col.g = 1.0;
        col.b = 1.0;
    } else {
        float sl = float(n) - log2(log2(a*a+b*b)) + 4.0;

        float al = smoothstep( -0.1, 0.0, sin(0.5*6.2831*iTime ) );
        float l = mix( float(n), sl, al );
        col += 0.5 + 0.5*cos( 3.0 + l*0.15 + vec3(0.0,0.6,1.0));
    }

    fragColor = vec4(col,1.0);
}