#version 430
layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

struct Particle {
    vec2 pos;
    float radius_effect;
    float radius;
    vec4 color;
    vec2 vel;
    vec2 acc;
    // vec4 mass;
};

layout(std430, binding=0) buffer particles_in {Particle particles[];} In;
layout(std430, binding=1) buffer particles_out {Particle particles[];} Out;
// layout(std430, binding=2) buffer grids_in {Grid grids[];} Grid_in;
// layout(std430, binding=3) buffer grids_out {Grid grids[];} Grid_out;

const float collisionDamping = .5;

void main() {
    int idx = int(gl_GlobalInvocationID);
    Particle p1 = In.particles[idx];
    // TODO Repel when **near** side
    if (p1.pos.x+p1.radius >= WIN_WIDTH) {p1.pos.x = WIN_WIDTH-p1.radius;p1.vel.x *= -collisionDamping;}
    if (p1.pos.y+p1.radius >= WIN_HEIGHT) {p1.pos.y = WIN_HEIGHT-p1.radius;p1.vel.y *= -collisionDamping;}
    if (p1.pos.x-p1.radius <= 0) {p1.pos.x = 0+p1.radius;p1.vel.x *= -collisionDamping;}
    if (p1.pos.y-p1.radius <= 0) {p1.pos.y = 0+p1.radius;p1.vel.y *= -collisionDamping;}
    // p1.vel.y -= .1;
    float neighbors = 0;
    
    for (int i=0; i < In.particles.length(); i++) {
        if (i == idx) {continue;}
        Particle p2 = In.particles[i];
        vec2 dir = p1.pos.xy - p2.pos.xy;
        float distSquared = dot(dir,dir);
        if (distSquared < pow(p1.radius_effect, 2)) {
            float force = pow(pow(p1.radius_effect, 2)-distSquared, 3)/(10000000000000.*p1.radius_effect);
            p1.vel += force * normalize(dir);
            neighbors += pow(p1.radius_effect, 2)-distSquared;
        }
    }
    p1.color.g = 1.0-neighbors/(p1.radius_effect*10000.);
    p1.color.b = 1.0-neighbors/(p1.radius_effect*10000.);

    p1.pos += p1.vel;
    p1.vel *= .9;

    Out.particles[idx] = p1;
}


    // for (int i=0; i < In.particles.length(); i++) {
    //     Particle p2 = In.particles[i];

    //     vec2 dir = p1.pos.xy - p2.pos.xy;
    //     float distanceSquared = dot(dir, dir);
        
    //     if (distanceSquared < pow(p1.radius+p2.radius, 2)) { // Collision
    //         //TODO Check if not more than 10 collisions
    //         collisions[collision_count] = i;
    //         collision_count += 1;
    //         continue;
    //     }

    //     float gravityStrength = pow(10, 3)*p1.charge*p2.charge;
    //     float force = min(0.02, gravityStrength / distanceSquared);
    //     dir = normalize(dir);
    //     p1.vel.xy += (dir * force) / p1.radius;
    // }