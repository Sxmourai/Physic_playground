struct Sphere {
    vec3 pos;
    float radius;
    vec3 color;
    bool light_source;
};

struct Photon {
    vec3 pos;
    vec3 vel;
    vec3 color;
};

uint random(uint seed) {
    seed = seed * uint(747796405) + uint(2891336453);
    uint result = ((seed >> ((seed >> 28) + uint(4))) ^ seed) * uint(2778037373);
    result = (result >> 22) ^ result;
    return result / uint(4294967295);
}

vec3 rnd_direction(uint seed) {
    uint r = random(seed);
    uint g = random(r);
    uint b = random(g);
    return vec3(float(r), float(g), float(b));
}

vec3 random_in_hemisphere(vec3 normal, uint seed) {
    vec3 dir = rnd_direction(seed);
    return dir * sign(dot(normal, dir));
}



void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord/iResolution.xy)-.5;
    uv.y /= iResolution.x/iResolution.y;
    uint pixel_idx = uint(fragCoord.y * iResolution.x + fragCoord.x);
    vec3 dir = normalize(vec3(uv.xy, 1.0));
    vec3 orig = vec3(0.0, 0.0, -5.0);
    Photon ray = Photon(orig, dir, vec3(0.0));
    int time_steps = 0;
    Sphere spheres[] = Sphere[](
        Sphere(vec3(-1.5, 0., 3.),1.5, vec3(0.5, 1., 0.5), true)
        ,Sphere(vec3(0., 0., 5.), .5, vec3(.5, 0.25, 0.5), false)
        ,Sphere(vec3(0., -100., 5.), 95., vec3(1.0, 1., 0.5), true)
        ,Sphere(vec3(0., 1000., 5.), 700., vec3(1.0, 1., 0.5), true)
        ,Sphere(vec3(2.5, 0., 6.),2.5, vec3(0.5, 1., 0.5), true)
    );
    float closest_hit = 10000.;
    bool hit_light = false;
    while (hit_light==false) {
        ray.pos += ray.vel;
        for (int i = 0; i < spheres.length(); i++) {
            Sphere sphere = spheres[i];
            vec3 dst = ray.pos - sphere.pos;
            float a = dot(ray.vel, ray.vel);
            float b = 2 * dot(dst, ray.vel);
            float c = dot(dst,dst) - sphere.radius*sphere.radius;
            float discriminant = b*b - 4*a*c;

            // Discriminant < 0 -> No intersection
            if (discriminant >= 0) {
                float dst = (-b - sqrt(discriminant)) / (2*a);
                // Ignore intersections behind ray
                if (dst>=0 && dst < closest_hit) {
                    vec3 hit_point = ray.pos + ray.vel * dst;
                    vec3 normal = normalize(hit_point - sphere.pos);
                    ray.color = normalize(sphere.color + random_in_hemisphere(normal, pixel_idx+uint(iTime)));
                    closest_hit = dst;
                    if (sphere.light_source) {  
                        hit_light = true;
                        // break;
                    } else {
                        ray.vel = normalize(random_in_hemisphere(normal, pixel_idx+uint(iTime)));
                    }
                }
            }
        }
        // if (ray.pos.z > 100.) {
        //     ray.color = vec3(0.);
        //     break;
        // }
        if (time_steps > 1000) {
            ray.color = vec3(0.);
            break;
        }
        time_steps += 1;
    }


    fragColor = vec4(ray.color, 1.0);
}
            // float force = .0001*sphere.charge/dst_sq;
            // vec3 dir = normalize(dst);
            // ray.vel += force * dir;

// Anti aliasing

    // ray.dir.x += randrange(fragCoord.y+sample,-0.0005, 0.0005); // Pseudo random
    //     ray.dir.y += randrange(fragCoord.x+sample,-0.0005, 0.0005);
        // color += get_color(ray);