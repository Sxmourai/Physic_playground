#version 430
layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

struct Particle {
    vec2 pos;
    float radius_effect;
    float radius;
    vec4 color;
    vec2 vel;
    vec2 acc;
};

layout(std430, binding=0) buffer particles_in {Particle particles[];} In;
layout(std430, binding=3) buffer densities_out {float densities[];} Out;

float smoothKernel(float radius_effect, float dst) {
    return pow(radius_effect - dst, 2);
}

void main() {
    int idx = int(gl_GlobalInvocationID);
    Particle p1 = In.particles[idx];
    float density = 0;

    for (int i=0; i < In.particles.length(); i++) {
        if (i == idx) {continue;}
        Particle p2 = In.particles[i];
        vec2 dir = p1.pos.xy - p2.pos.xy;
        float distSquared = dot(dir,dir);
        float dist = sqrt(distSquared);
        if (dist < p1.radius_effect) {
            float influence = smoothKernel(p1.radius_effect, dist);
            density += 1.0 * influence;
        }
    }

    Out.densities[idx] = density;
}