// uniform vec3 iResolution;
// uniform float iTime;
// uniform float iTimeDelta;
// uniform float iFrame;
// uniform float iChannelTime[4];
// uniform vec4 iMouse;
// uniform vec4 iDate;
// uniform float iSampleRate;
// uniform vec3 iChannelResolution[4];
// // uniform samplerXX iChanneli;

struct Sphere {
    vec3 pos;
    float radius;
};

struct Ray {
    vec3 pos;
    vec3 dir;
};

struct HitRecord {
    bool valid;
    vec3 pos;
    vec3 normal;
    float t;
    bool front_face;
};

HitRecord set_face_normal(HitRecord rec, Ray ray, vec3 outward_normal) {
    // Sets the hit record normal vector.
    // NOTE: the parameter `outward_normal` is assumed to have unit length.

    rec.front_face = dot(ray.dir, outward_normal) < 0;
    rec.normal = rec.front_face ? outward_normal : -outward_normal;
    return rec;
}

vec3 at(Ray ray, float t) {
    return ray.pos + ray.dir*t;
};


HitRecord hit_sphere(Sphere sphere, Ray ray, float ray_tmax, float ray_tmin) {
    HitRecord invalid;
    vec3 pos = sphere.pos;
    float radius = sphere.radius;
    vec3 dst = pos - ray.pos;
    float len_sq = dot(ray.dir, ray.dir);
    float b = dot(ray.dir, dst);
    float c = dot(dst, dst) - radius*radius;
    float discrim = b*b - len_sq*c;

    if (discrim < 0) {
        return invalid;
    }
    float sqrtd = sqrt(discrim);
    // Find the nearest root that lies in the acceptable range.
    float root = (b - sqrtd) / max(.1, len_sq);
    if (root <= ray_tmin || root >= ray_tmax) {
        root = (b + sqrtd) / max(.1, len_sq);
        if (root <= ray_tmin || root >= ray_tmax) {
            return invalid;
        }
    }
    vec3 rec_pos = at(ray, root);
    HitRecord rec = HitRecord(true, rec_pos, (rec_pos - pos) / radius, root, false);
    vec3 outward_normal = (rec_pos - pos) / radius;
    rec = set_face_normal(rec, ray, outward_normal);
    return rec;
}
// Returns pseudo random between 0-1
float rand(float seed){
    return fract(sin(dot(vec2(seed,seed*seed), vec2(12.9898, 78.233))) * 43758.5453);
}

float randrange(float seed, float min, float max) {
    return rand(seed)*(max-min) + min;
}
vec3 random_in_unit_sphere(float seed) {
    for (int i=0;i<10000;i++) { // TODO Optimize maybe ?
        vec3 p = vec3(randrange(seed+i, -1., 1.),randrange(seed+1+i, -1., 1.),randrange(seed+2+i, -1., 1.));
        if (dot(p,p) < 1) {return p;}
    }
}

vec3 random_on_hemisphere(float seed, vec3 normal) {
    vec3 on_unit_sphere = normalize(random_in_unit_sphere(seed));
    if (dot(on_unit_sphere, normal) > 0.) { // In same hemisphere as normal
        return on_unit_sphere;
    } else {
        return -on_unit_sphere;
    }
}

// #define FLT_MAX 3.402823466e+38
// #define FLT_MIN 1.175494351e-38
// #define DBL_MAX 1.7976931348623158e+308
// #define DBL_MIN 2.2250738585072014e-308

vec3 get_color(Ray ray) {
    vec3 color = vec3(0.0);
    Sphere spheres[] = Sphere[](
        Sphere(vec3(0., 0., 2.), 0.5),
        Sphere(vec3(1.5, 0., 2.), 0.35),
        Sphere(vec3(0,-100.5,-1), 100)
    );
    int depth = 50;
    while (depth >= 0) {
        HitRecord temp_rec;
        bool hit_anything = false;
        float closest_so_far = 3.402823466e+38;

        for (int i=0;i<spheres.length();i++) {
            HitRecord rec = hit_sphere(spheres[i], ray, closest_so_far, 0.001);
            if (rec.valid == true) {
                hit_anything = true;
                closest_so_far = rec.t;
                // rec = temp_red
                temp_rec = rec;
            }
        }
        if (hit_anything==true) {
            vec3 dir = temp_rec.normal + normalize(random_in_unit_sphere(dot(ray.pos, ray.dir)));
            ray = Ray(temp_rec.pos, dir);
        } else {
            float a = 0.5*(ray.dir.y+1.0);
            color = (1.0-a)*vec3(1.0)+a*vec3(0.5,0.7, 1.0);
        }
        depth -= 1;
    }

    return color;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord/iResolution.xy) - 0.5;
    uv.y /= iResolution.x/iResolution.y;
    vec3 dir = vec3(uv.xy, 1.0);
    vec3 orig = vec3(0.0, 0.0, -3.0);

    vec3 color;
    int samples_per_pixel = 10;
    for (int sample=0;sample<samples_per_pixel;sample++) {
        Ray ray = Ray(orig, dir);
        ray.dir.x += randrange(fragCoord.y+sample,-0.0005, 0.0005); // Pseudo random
        ray.dir.y += randrange(fragCoord.x+sample,-0.0005, 0.0005);
        color += get_color(ray);
    }
    color /= samples_per_pixel;

    fragColor = vec4(color, 1.0);
}