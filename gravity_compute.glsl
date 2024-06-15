#version 430

layout(local_size_x=COMPUTE_SIZE_X, local_size_y=COMPUTE_SIZE_Y) in;

//uniform vec2 screen_size;
//uniform vec2 force;
//uniform float frame_time;

struct Particle {
    vec2 pos;
    float charge;
    float radius;
    vec4 color;
    vec2 vel;
    vec2 acc;
    vec4 mass;
};

struct Grid {
    float avg_mass;
};
layout(std430, binding=0) buffer particles_in {Particle particles[];} In;
layout(std430, binding=1) buffer particles_out {Particle particles[];} Out;
layout(std430, binding=2) buffer grids_in {Grid grids[];} Grid_in;
layout(std430, binding=3) buffer grids_out {Grid grids[];} Grid_out;

void solveCollisions(Particle p1, int collisions[10], int collision_count) {
    for (int i=0;i<collision_count;i++) {
        Particle p2 = In.particles[collisions[i]];
        
        vec2 dir = p1.pos.xy - p2.pos.xy;
        float distanceSquared = dot(dir, dir);
        float dist = sqrt(distanceSquared);
        float delta = p1.radius+p2.radius - dist;
        p1.pos += 0.5 * delta * (dir/dist);
        In.particles[i].pos -= 0.5 * delta * (dir/dist);
        vec2 v2 = p2.vel;
        float m2 = p2.radius;
        p1.vel.x = ((p1.vel.x * (p1.radius - m2) + (2 * m2 * v2.x)) / (m2 + p1.radius))*20.;
        p1.vel.y = ((p1.vel.y * (p1.radius - m2) + (2 * m2 * v2.y)) / (m2 + p1.radius))*20.;
    }
}

void main() {
    int curparticleIndex = int(gl_GlobalInvocationID);
    Particle p1 = In.particles[curparticleIndex];

    int n = WIN_WIDTH/GRID_ROWS;
    int grid_x = int(n * round(p1.pos.x / float(n)));
    n = WIN_HEIGHT/GRID_COLS;
    int grid_y = int(n * round(p1.pos.y / float(n)));

    int ix = grid_x/GRID_ROWS;
    int iy = grid_y/GRID_COLS;

    if (p1.pos.x+p1.vel.x+p1.radius >= WIN_WIDTH) {p1.pos.x = WIN_WIDTH-p1.radius;p1.vel.x*=-.5;}
    if (p1.pos.y+p1.vel.y+p1.radius >= WIN_HEIGHT) {p1.pos.y = WIN_HEIGHT-p1.radius;p1.vel.y*=-.5;}
    if (p1.pos.x+p1.vel.x-p1.radius <= 0) {p1.pos.x = 0+p1.radius;p1.vel.x*=-.5;}
    if (p1.pos.y+p1.vel.y-p1.radius <= 0) {p1.pos.y = 0+p1.radius;p1.vel.y*=-.5;}

    p1.mass.xyzw += vec4(1.0);

    int collisions[10];
    int collision_count = 0;

    for (int i=0; i < In.particles.length(); i++) {
        // If enabled, this will keep the star from calculating gravity on itself
        // However, it does slow down the calcluations do do this check.
         if (i == curparticleIndex)
             continue;

        // float dist = distance(In.particles[i].pos.xyzw.xy, p.xy);
        // float distanceSquared = dist * dist;

        Particle p2 = In.particles[i];

        vec2 dir = p1.pos.xy - p2.pos.xy;
        float distanceSquared = dot(dir, dir);
        
        if (distanceSquared < pow(p1.radius+p2.radius, 2)) { // Collision
            //TODO Check if not more than 10 collisions
            collisions[collision_count] = i;
            // collision_count += 1;
            continue;
        }

        float gravityStrength = pow(10, 3)*p1.charge*p2.charge;
        float force = min(0.02, gravityStrength / distanceSquared);
        dir = normalize(dir);
        p1.acc.xy += (dir * force) / p1.radius;
    }


    p1.vel += p1.acc;
    p1.acc = vec2(0.);

    solveCollisions(p1, collisions, collision_count);

    p1.pos += p1.vel;


    Particle out_particle = p1;
    // out_particle.pos = p;
    // out_particle.vel = v;
    Out.particles[curparticleIndex] = out_particle;
}
