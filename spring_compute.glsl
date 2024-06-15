#version 430

layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

struct Particle {
    vec2 pos;
    float _;
    float radius;
    vec4 color;
    vec4 vel;
};

struct Spring {
    float p1; // indexes to particles
    float p2;
};


layout(std430, binding=0) buffer particles_in {Particle particles[];} PIn;
layout(std430, binding=1) buffer particles_out {Particle particles[];} POut;
layout(std430, binding=2) buffer springs_in {Spring springs[];} SIn;
layout(std430, binding=3) buffer springs_out {Spring springs[];} SOut;

void main() {
    int idx = int(gl_GlobalInvocationID);
    Spring spring = SIn.springs[idx];
    Particle p1 = PIn.particles[int(spring.p1)];
    Particle p2 = PIn.particles[int(spring.p2)];
    float dist = distance(p1.pos.xy, p2.pos.xy);
    float desired = 100.;
    float force = (dist - desired)/100000000000000.;
    vec2 dir = normalize(p1.pos.xy - p2.pos.xy);
    // p1.vel.xy -= force * dir;
    // p2.vel.xy += force * dir;

    p1.pos.xy += p1.vel.xy;
    p2.pos.xy += p2.vel.xy;
    p1.vel.xy *= .9;
    p2.vel.xy *= .9;

    p1.color.g = 1.0-length(p1.vel.xy)/20.;
    p1.color.b = 1.0-length(p1.vel.xy)/20.;
    p2.color.g = 1.0-length(p2.vel.xy)/20.;
    p2.color.b = 1.0-length(p2.vel.xy)/20.;

    SOut.springs[idx] = spring;
    POut.particles[int(spring.p1)] = p1;
    POut.particles[int(spring.p2)] = p2;
}
